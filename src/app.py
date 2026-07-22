"""blackjack-vision main loop.

  python -m src.app                # run (windowed unless app.yaml says fullscreen)
  python -m src.app --fullscreen   # force fullscreen (Pi kiosk)
  python -m src.app --selftest     # headless smoke test: config+model+UI, no camera
  python -m src.app --camera-test  # open the webcam, report FPS, save a frame
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

from .config import AppConfig, load_app_config
from .engines.ev import hand_ev
from .engines.hilo import bet_units
from .engines.rules import Rules, load_rules
from .engines.strategy import decide
from .game_state import dealer_up_key, hand_value, is_blackjack, is_bust
from .session import ShoeSession
from .stable import StableTracker
from .tracker import RoundTracker, SessionStats
from .zones import Zone

ROOT = Path(__file__).resolve().parents[1]
RULES_PATH = ROOT / "config" / "rules.yaml"
NEW_SHOE_CONFIRM_SECONDS = 2.5
EV_CACHE_MAX = 256
REAL_ACTIONS = ("HIT", "STAND", "DOUBLE", "SPLIT", "SURRENDER")


def compute_decision(state, rules: Rules):
    """(action_name, player_total_str, dealer_up_str) for the current table."""
    player = state.cards(Zone.PLAYER)
    dealer = state.cards(Zone.DEALER)
    if len(player) < 2 or len(dealer) != 1:
        return None, "", ""
    total = hand_value(player)
    if is_blackjack(player):
        return "BLACKJACK!", str(total), dealer_up_key(dealer[0])
    if is_bust(player):
        return "BUST", str(total), dealer_up_key(dealer[0])
    decision = decide(player, dealer[0], rules)
    return decision.action.value, str(total), dealer_up_key(dealer[0])


def compute_ev(state, rules, session, cache):
    """(ev_dict, win_prob) for the current hand, cached per table state."""
    player = state.cards(Zone.PLAYER)
    dealer = state.cards(Zone.DEALER)
    if len(player) < 2 or len(dealer) != 1 or is_bust(player) or is_blackjack(player):
        return {}, None
    comp = session.remaining_composition()
    if sum(comp.values()) == 0:
        return {}, None  # shoe exhausted / overcounted — EV meaningless, don't crash
    key = (player, dealer[0], session.count.cards_seen, rules)
    if key not in cache:
        if len(cache) >= EV_CACHE_MAX:
            cache.clear()
        cache[key] = hand_ev(player, dealer[0], rules, comp)
    result = cache[key]
    return (
        {a: o.ev for a, o in result.actions.items()},
        result.best_outcome.p_win,
    )


def run(cfg: AppConfig, rules: Rules, fullscreen: bool,
        run_seconds: float = 0, log_events: bool = False) -> int:
    from .capture import Camera
    from .detector import CardDetector
    from .ui.dashboard import Dashboard, ViewModel
    from .ui.settings import SettingsScreen, save_rules

    # Camera opens LAST so a model/UI failure can't leak the device handle.
    detector = CardDetector(str(ROOT / cfg.model_path), cfg.confidence, cfg.zone_split)
    tracker = StableTracker(cfg.confirm_frames, cfg.forget_frames,
                            cfg.merge_dist_px, cfg.merge_scale)
    session = ShoeSession(decks=rules.decks)
    rounds = RoundTracker()
    stats = SessionStats()
    dashboard = Dashboard(fullscreen=fullscreen)
    camera = Camera(cfg.camera_index, cfg.camera_width, cfg.camera_height)

    paused = False
    status = ""
    status_until = 0.0
    new_shoe_armed_until = 0.0
    fps = 0.0
    state = tracker.update([])
    ev_cache: dict = {}

    def flash(message: str, seconds: float = 2.0) -> None:
        nonlocal status, status_until
        status, status_until = message, time.time() + seconds

    def end_hand(result) -> None:
        if result is not None:
            stats.record_result(result)
            flash(f"hand: {result.outcome.value}")
        # Note: the StableTracker is deliberately NOT reset — cards physically
        # still on the felt stay tracked, and the session marks them stale so
        # they can never be counted twice (see ShoeSession docstring).
        session.end_hand()

    started = time.time()
    try:
        while True:
            if run_seconds and time.time() - started > run_seconds:
                print(f"run-seconds elapsed; final fps ~{fps:.1f}")
                return 0
            loop_start = time.perf_counter()
            for intent in dashboard.poll():
                if intent == "QUIT":
                    return 0
                if intent == "PAUSE":
                    paused = not paused
                if intent == "END_HAND":
                    end_hand(rounds.finish())
                if intent == "NEW_SHOE":
                    if time.time() < new_shoe_armed_until:
                        session.new_shoe()
                        tracker.reset()
                        rounds.reset()
                        ev_cache.clear()
                        new_shoe_armed_until = 0.0
                        flash("new shoe — count reset")
                    else:
                        new_shoe_armed_until = time.time() + NEW_SHOE_CONFIRM_SECONDS
                        flash("press N again to confirm new shoe",
                              NEW_SHOE_CONFIRM_SECONDS)
                if intent == "SETTINGS":
                    settings = SettingsScreen(dashboard.screen, rules)
                    while not settings.done:
                        settings.handle_events()
                        settings.render()
                        time.sleep(0.03)
                    if settings.quit_requested:
                        return 0
                    if settings.saved is not None:
                        try:
                            save_rules(settings.saved, RULES_PATH)
                            rules = load_rules(RULES_PATH)  # round-trip = validation
                        except OSError as exc:
                            flash(f"save failed: {exc}", 4.0)
                        else:
                            session = ShoeSession(decks=rules.decks)
                            tracker.reset()
                            rounds.reset()
                            ev_cache.clear()
                            if not rules.uses_multideck_chart:
                                flash(f"saved — note: charts assume 4-8 decks, "
                                      f"you set {rules.decks}", 4.0)
                            else:
                                flash("rules saved — new shoe started")

            frame = camera.read()
            boxes = []
            if not paused and frame is not None:
                detections = detector.detect(frame)
                state = tracker.update(detections,
                                       split_y=frame.shape[0] * cfg.zone_split)
                session.apply_events(state.events)
                boxes = [(d.box, f"{d.card} {d.zone.value[0]}") for d in detections]
                if log_events and state.events:
                    stamp = time.strftime("%H:%M:%S")
                    for e in state.events:
                        print(f"[{stamp}] {e.kind.value} {e.card} {e.zone.value} "
                              f"#{e.instance}", flush=True)
                    print(f"[{stamp}] table: dealer={[str(c) for c in state.cards(Zone.DEALER)]} "
                          f"player={[str(c) for c in state.cards(Zone.PLAYER)]} "
                          f"running={session.count.running}", flush=True)
                    _save_evidence_frame(frame, detections, cfg)
                end_of_round = rounds.update(state)
                if end_of_round is not None:
                    end_hand(end_of_round)
            else:
                # paused, or camera dropped a frame: freeze the table state —
                # a camera glitch must never look like cards leaving the felt
                time.sleep(0.03)

            action, player_total, dealer_up = compute_decision(state, rules)
            # observe EVERY frame (advice may be None mid-transition) so a hit
            # that confirms late still resolves the pending decision correctly
            stats.observe(action, len(state.cards(Zone.PLAYER)))
            ev_dict, win_prob = compute_ev(state, rules, session, ev_cache)

            if time.time() > status_until:
                status = ""
            count = session.count
            units = bet_units(count.true_count_floor, cfg.bet_ramp)
            vm = ViewModel(
                frame=frame,
                boxes=boxes,
                zone_split_y=int(frame.shape[0] * cfg.zone_split) if frame is not None else 0,
                player_cards=[str(c) for c in state.cards(Zone.PLAYER)],
                dealer_cards=[str(c) for c in state.cards(Zone.DEALER)],
                action=action,
                player_total=player_total,
                dealer_up=dealer_up,
                running_count=count.running,
                true_count=count.true_count,
                decks_remaining=count.decks_remaining,
                bet_units=units,
                bet_amount=units * cfg.bet_unit,
                hands_played=session.hands_played,
                ev=ev_dict,
                win_prob=win_prob,
                stats_line=stats.summary_line() if stats.hands else "",
                status=status,
                fps=fps,
                paused=paused,
                show_fps=cfg.show_fps,
            )
            dashboard.render(vm)

            elapsed = time.perf_counter() - loop_start
            fps = 0.9 * fps + 0.1 * (1.0 / elapsed) if elapsed > 0 else fps
    finally:
        camera.release()
        dashboard.close()


_evidence_count = 0


def _save_evidence_frame(frame, detections, cfg, limit: int = 20) -> None:
    """Annotated snapshots for the verification log (captures/, gitignored)."""
    global _evidence_count
    if _evidence_count >= limit:
        return
    import cv2

    out = ROOT / "captures"
    out.mkdir(exist_ok=True)
    annotated = frame.copy()
    for d in detections:
        x1, y1, x2, y2 = (int(v) for v in d.box)
        cv2.rectangle(annotated, (x1, y1), (x2, y2), (80, 220, 120), 2)
        cv2.putText(annotated, f"{d.card} {d.confidence:.2f}", (x1, max(y1 - 6, 12)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (80, 220, 120), 2)
    _evidence_count += 1
    cv2.imwrite(str(out / f"live_{_evidence_count:02d}.jpg"), annotated)


def selftest(cfg: AppConfig, rules: Rules) -> int:
    """Headless smoke test: config, model, engines, UI render — no camera."""
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    import numpy as np

    from .cards import card
    from .detector import CardDetector
    from .engines.ev import full_composition
    from .ui.dashboard import Dashboard, ViewModel

    print(f"rules: {rules}")
    print(f"app config: {cfg}")

    detector = CardDetector(str(ROOT / cfg.model_path), cfg.confidence, cfg.zone_split)
    fake = np.zeros((cfg.camera_height, cfg.camera_width, 3), dtype=np.uint8)
    detections = detector.detect(fake)
    print(f"model loaded; blank-frame detections: {len(detections)} (expect 0)")

    # engines end-to-end on a scripted hand: 10,6 v 10 should say HIT with EV
    result = hand_ev((card("10S"), card("6H")), card("10D"), rules,
                     full_composition(rules.decks))
    evs = {a: round(o.ev, 3) for a, o in result.actions.items()}
    print(f"EV check 16 v 10: best={result.best} {evs}")

    tracker = StableTracker(cfg.confirm_frames, cfg.forget_frames, cfg.merge_dist_px)
    session = ShoeSession(decks=rules.decks)
    state = tracker.update([])
    action, player_total, dealer_up = compute_decision(state, rules)

    dashboard = Dashboard(fullscreen=False)
    count = session.count
    vm = ViewModel(
        frame=fake, action=action, player_total=player_total, dealer_up=dealer_up,
        running_count=count.running, true_count=count.true_count,
        decks_remaining=count.decks_remaining, status="selftest",
    )
    for _ in range(3):
        dashboard.render(vm)
    dashboard.close()
    print("selftest OK: config + model + engines + UI render all work")
    return 0


def camera_test(cfg: AppConfig) -> int:
    import cv2

    from .capture import Camera

    camera = Camera(cfg.camera_index, cfg.camera_width, cfg.camera_height)
    print(f"camera {cfg.camera_index} open at {camera.resolution}")
    frames = 0
    t0 = time.perf_counter()
    last = None
    while time.perf_counter() - t0 < 3.0:
        frame = camera.read()
        if frame is not None:
            frames += 1
            last = frame
    camera.release()
    seconds = time.perf_counter() - t0
    print(f"captured {frames} frames in {seconds:.1f}s ({frames / seconds:.1f} fps)")
    if last is not None:
        out = ROOT / "captures"
        out.mkdir(exist_ok=True)
        path = out / "camera_test.jpg"
        cv2.imwrite(str(path), last)
        print(f"saved {path}")
        return 0
    print("no frames captured — check the webcam")
    return 1


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="blackjack-vision")
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--camera-test", action="store_true")
    parser.add_argument("--fullscreen", action="store_true")
    parser.add_argument("--run-seconds", type=float, default=0,
                        help="exit automatically after N seconds (testing)")
    parser.add_argument("--log-events", action="store_true",
                        help="print card ADDED/REMOVED events and save annotated frames")
    args = parser.parse_args(argv)

    cfg = load_app_config(ROOT / "config" / "app.yaml")
    rules = load_rules(RULES_PATH)
    if not rules.uses_multideck_chart:
        print("note: strategy charts are the 4-8 deck tables; "
              f"rules.yaml says decks={rules.decks} — advice may be slightly off")

    if args.selftest:
        return selftest(cfg, rules)
    if args.camera_test:
        return camera_test(cfg)
    return run(cfg, rules, fullscreen=args.fullscreen or cfg.fullscreen,
               run_seconds=args.run_seconds, log_events=args.log_events)


if __name__ == "__main__":
    sys.exit(main())
