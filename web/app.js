/* blackjack-vision web — in-browser port of the Python trainer.
 *
 * Detection: ONNX Runtime Web running the same YOLOv8n weights (960px).
 * Strategy: chart JSON generated from the chart-fixture-verified Python
 * engine (scripts/export_web_assets.py) — the browser never re-derives it.
 * Tracking/counting: compact ports of src/stable.py + src/session.py:
 * zone-blind corner clustering, size-scaled merge, confirm/decay debounce,
 * deck-count copy cap, returnable-pool count ledger.
 */
"use strict";

// ---------- tunables (mirror config/app.yaml) ----------
const IMGSZ = 960;
const CONF = 0.5;
const IOU_NMS = 0.45;
const CONFIRM_FRAMES = 4;
const FORGET_FRAMES = 12;
const HEAL_PER_SIGHTING = 2;
const MERGE_DIST = 140;
const MERGE_SCALE = 4.0;
const BET_RAMP = { 1: 1, 2: 2, 3: 4, 4: 8, 5: 12 };

const TEN_RANKS = new Set(["10", "J", "Q", "K"]);
const PLUS = new Set(["2", "3", "4", "5", "6"]);
const MINUS = new Set(["10", "J", "Q", "K", "A"]);

// ---------- card helpers (port of src/cards.py + game_state.py) ----------
function parseClass(name) {
  const m = /^(10|[2-9]|[AJQK])([SHDC])$/.exec(name.toUpperCase());
  return m ? { rank: m[1], suit: m[2], id: m[1] + m[2] } : null; // BACK/JOKER -> null
}
function cardValue(rank) {
  if (rank === "A") return 11;
  return TEN_RANKS.has(rank) ? 10 : parseInt(rank, 10);
}
function handValue(cards) {
  let total = 0, aces = 0;
  for (const c of cards) { total += cardValue(c.rank); if (c.rank === "A") aces++; }
  while (total > 21 && aces) { total -= 10; aces--; }
  return { total, soft: aces > 0 };
}
function isPair(cards) {
  if (cards.length !== 2) return false;
  const [a, b] = cards;
  return a.rank === b.rank || (TEN_RANKS.has(a.rank) && TEN_RANKS.has(b.rank));
}
function pairRank(cards) { return TEN_RANKS.has(cards[0].rank) ? "10" : cards[0].rank; }
function upKey(card) { return card.rank === "A" ? "A" : (TEN_RANKS.has(card.rank) ? "10" : card.rank); }
function hiloValue(rank) { return PLUS.has(rank) ? 1 : (MINUS.has(rank) ? -1 : 0); }

// ---------- strategy (cell tables from Python; resolution mirrors decide()) ----------
let CHART = null;
function decide(player, dealerUp, rules) {
  const v = handValue(player);
  if (player.length === 2 && v.total === 21) return "BLACKJACK!";
  if (v.total > 21) return "BUST";
  const set = rules.h17 ? CHART.H17 : CHART.S17;
  const up = upKey(dealerUp);
  const two = player.length === 2;
  const canDouble = two;
  const canSurrender = rules.ls && two;
  let cell = null, splittable = false;
  if (two && isPair(player)) {
    const row = set.pairs[pairRank(player)];
    if (row) { cell = row[up]; splittable = true; }
  }
  if (!cell) {
    if (v.soft) cell = v.total === 12 ? "H" : set.soft[String(Math.min(v.total, 20))][up];
    else if (v.total >= 18) cell = "S";
    else cell = set.hard[String(Math.max(v.total, 5))][up];
  }
  switch (cell) {
    case "H": return "HIT";
    case "S": return "STAND";
    case "Dh": return canDouble ? "DOUBLE" : "HIT";
    case "Ds": return canDouble ? "DOUBLE" : "STAND";
    case "P": return "SPLIT";
    case "Ph": return (splittable && rules.das) ? "SPLIT" : "HIT";
    case "Rh": return canSurrender ? "SURRENDER" : "HIT";
    case "Rs": return canSurrender ? "SURRENDER" : "STAND";
    case "Rp": return canSurrender ? "SURRENDER" : "SPLIT";
    default: return "…";
  }
}

// ---------- tracker (port of src/stable.py) ----------
function boxCenter(b) { return [(b[0] + b[2]) / 2, (b[1] + b[3]) / 2]; }
function boxDim(b) { return Math.max(b[2] - b[0], b[3] - b[1]); }
let mergeFloor = MERGE_DIST; // scaled to the camera's real width each frame
function mergeable(a, b) {
  const [ax, ay] = boxCenter(a), [bx, by] = boxCenter(b);
  const dist = Math.hypot(ax - bx, ay - by);
  return dist <= Math.max(mergeFloor, MERGE_SCALE * Math.max(boxDim(a), boxDim(b)));
}
function clusterBoxes(boxes) {
  const clusters = [];
  boxes.forEach((box, i) => {
    const hit = clusters.find(c => c.some(j => mergeable(boxes[i], boxes[j])));
    if (hit) hit.push(i); else clusters.push([i]);
  });
  let merged = true;
  while (merged) {
    merged = false;
    outer: for (let a = 0; a < clusters.length; a++)
      for (let b = a + 1; b < clusters.length; b++)
        if (clusters[a].some(i => clusters[b].some(j => mergeable(boxes[i], boxes[j])))) {
          clusters[a].push(...clusters[b]); clusters.splice(b, 1);
          merged = true; break outer;
        }
  }
  return clusters;
}

class Tracker {
  constructor() { this.tracks = new Map(); this.nextUid = new Map(); }
  reset() { this.tracks.clear(); this.nextUid.clear(); }
  update(detections, splitY, maxCopies) {
    // zone-blind clustering per card class; cluster centroid decides the zone
    const byCard = new Map();
    for (const d of detections) {
      if (!byCard.has(d.card.id)) byCard.set(d.card.id, []);
      byCard.get(d.card.id).push(d);
    }
    const observed = new Map(); // "AS|P" -> count
    for (const [cardId, dets] of byCard) {
      const boxes = dets.map(d => d.box);
      for (const cluster of clusterBoxes(boxes)) {
        const cy = cluster.reduce((s, i) => s + boxCenter(boxes[i])[1], 0) / cluster.length;
        const zone = cy < splitY ? "D" : "P";
        const key = cardId + "|" + zone;
        observed.set(key, (observed.get(key) || 0) + 1);
      }
    }
    // physical cap: at most `decks` copies of one card across zones
    const perCard = new Map();
    for (const [key, n] of observed) {
      const cardId = key.split("|")[0];
      perCard.set(cardId, (perCard.get(cardId) || 0) + n);
    }
    for (const [cardId, total] of perCard) {
      let excess = total - maxCopies;
      if (excess <= 0) continue;
      const keys = [...observed.keys()].filter(k => k.startsWith(cardId + "|"))
        .sort((a, b) => this.confirmedCount(a) - this.confirmedCount(b));
      for (const k of keys) {
        if (excess <= 0) break;
        const trim = Math.min(excess, observed.get(k));
        observed.set(k, observed.get(k) - trim); excess -= trim;
      }
    }
    // debounce
    const events = [];
    const keys = new Set([...this.tracks.keys(), ...observed.keys()]);
    for (const key of keys) {
      if (!this.tracks.has(key)) this.tracks.set(key, []);
      const tracks = this.tracks.get(key);
      const seenN = observed.get(key) || 0;
      while (tracks.length < seenN) {
        const uid = this.nextUid.get(key) || 1;
        this.nextUid.set(key, uid + 1);
        tracks.push({ uid, streak: 0, missed: 0, confirmed: false });
      }
      tracks.forEach((t, idx) => {
        if (idx < seenN) {
          t.streak++;
          t.missed = Math.max(0, t.missed - HEAL_PER_SIGHTING);
          if (!t.confirmed && t.streak >= CONFIRM_FRAMES) {
            t.confirmed = true;
            events.push({ kind: "ADDED", key, uid: t.uid });
          }
        } else { t.missed++; t.streak = 0; }
      });
      const kept = tracks.filter(t => {
        if (t.confirmed && t.missed > FORGET_FRAMES) {
          events.push({ kind: "REMOVED", key, uid: t.uid }); return false;
        }
        return t.confirmed || t.missed === 0;
      });
      if (kept.length) this.tracks.set(key, kept); else this.tracks.delete(key);
    }
    const counts = new Map();
    for (const [key, tracks] of this.tracks) {
      const n = tracks.filter(t => t.confirmed).length;
      if (n) counts.set(key, n);
    }
    return { counts, events };
  }
  confirmedCount(key) {
    return (this.tracks.get(key) || []).filter(t => t.confirmed).length;
  }
}

// ---------- shoe session (port of src/session.py returnable-pool ledger) ----------
class Session {
  constructor(decks) { this.decks = decks; this.newShoe(); }
  newShoe() {
    this.running = 0; this.seen = 0; this.hands = 0;
    this.returnable = new Map(); this.stale = new Map(); this.active = new Map();
  }
  bump(map, k, d) { map.set(k, Math.max(0, (map.get(k) || 0) + d)); }
  applyEvents(events) {
    for (const e of events) {
      const cardId = e.key.split("|")[0];
      if (e.kind === "ADDED") {
        this.bump(this.active, cardId, 1);
        if ((this.returnable.get(cardId) || 0) > 0) { this.bump(this.returnable, cardId, -1); continue; }
        const rank = cardId.length === 3 ? cardId.slice(0, 2) : cardId[0];
        this.running += hiloValue(rank);
        this.seen++; this.countedThisHand = (this.countedThisHand || 0) + 1;
      } else {
        this.bump(this.active, cardId, -1);
        if ((this.stale.get(cardId) || 0) > 0) this.bump(this.stale, cardId, -1);
        else this.bump(this.returnable, cardId, 1);
      }
    }
  }
  endHand() {
    if (this.countedThisHand) this.hands++;
    this.countedThisHand = 0; this.returnable.clear();
    this.stale = new Map([...this.active].filter(([, n]) => n > 0));
  }
  get decksRemaining() {
    return Math.max(0.5, Math.floor((this.decks - this.seen / 52) * 2) / 2);
  }
  get trueCount() { return this.running / this.decksRemaining; }
  get betUnits() {
    const tc = Math.floor(this.trueCount);
    let units = Math.min(...Object.values(BET_RAMP));
    for (const t of Object.keys(BET_RAMP).map(Number).sort((a, b) => a - b))
      if (tc >= t) units = BET_RAMP[t];
    return units;
  }
}

// ---------- YOLO inference ----------
let ortSession = null;
let classNames = [];
const prep = document.createElement("canvas");
prep.width = IMGSZ; prep.height = IMGSZ;
const prepCtx = prep.getContext("2d", { willReadFrequently: true });

async function loadModel() {
  classNames = await (await fetch("assets/classes.json")).json();
  CHART = await (await fetch("assets/strategy.json")).json();
  const opts = {};
  try {
    ortSession = await ort.InferenceSession.create("assets/best.onnx",
      { executionProviders: ["webgpu", "wasm"] });
  } catch (e) {
    ortSession = await ort.InferenceSession.create("assets/best.onnx",
      { executionProviders: ["wasm"] });
  }
}

function letterbox(source, sw, sh) {
  const scale = Math.min(IMGSZ / sw, IMGSZ / sh);
  const dw = Math.round(sw * scale), dh = Math.round(sh * scale);
  const dx = Math.floor((IMGSZ - dw) / 2), dy = Math.floor((IMGSZ - dh) / 2);
  prepCtx.fillStyle = "#727272"; prepCtx.fillRect(0, 0, IMGSZ, IMGSZ);
  prepCtx.drawImage(source, 0, 0, sw, sh, dx, dy, dw, dh);
  const { data } = prepCtx.getImageData(0, 0, IMGSZ, IMGSZ);
  const n = IMGSZ * IMGSZ;
  const chw = new Float32Array(3 * n);
  for (let i = 0; i < n; i++) {
    chw[i] = data[i * 4] / 255;
    chw[n + i] = data[i * 4 + 1] / 255;
    chw[2 * n + i] = data[i * 4 + 2] / 255;
  }
  return { tensor: new ort.Tensor("float32", chw, [1, 3, IMGSZ, IMGSZ]), scale, dx, dy };
}

function iou(a, b) {
  const x1 = Math.max(a[0], b[0]), y1 = Math.max(a[1], b[1]);
  const x2 = Math.min(a[2], b[2]), y2 = Math.min(a[3], b[3]);
  const inter = Math.max(0, x2 - x1) * Math.max(0, y2 - y1);
  const areaA = (a[2] - a[0]) * (a[3] - a[1]);
  const areaB = (b[2] - b[0]) * (b[3] - b[1]);
  return inter / (areaA + areaB - inter + 1e-9);
}

async function detect(source, sw, sh) {
  const { tensor, scale, dx, dy } = letterbox(source, sw, sh);
  const out = await ortSession.run({ [ortSession.inputNames[0]]: tensor });
  const t = out[ortSession.outputNames[0]];       // [1, 4+C, N]
  const [, rows, anchors] = t.dims;
  const nc = rows - 4;
  const data = t.data;
  const cand = [];
  for (let i = 0; i < anchors; i++) {
    let best = 0, cls = -1;
    for (let c = 0; c < nc; c++) {
      const s = data[(4 + c) * anchors + i];
      if (s > best) { best = s; cls = c; }
    }
    if (best < CONF) continue;
    const cx = data[i], cy = data[anchors + i];
    const w = data[2 * anchors + i], h = data[3 * anchors + i];
    cand.push({
      score: best, cls,
      box: [(cx - w / 2 - dx) / scale, (cy - h / 2 - dy) / scale,
            (cx + w / 2 - dx) / scale, (cy + h / 2 - dy) / scale],
    });
  }
  cand.sort((a, b) => b.score - a.score);
  const keep = [];
  for (const c of cand) {                          // agnostic NMS
    if (keep.every(k => iou(k.box, c.box) < IOU_NMS)) keep.push(c);
  }
  const detections = [];
  for (const k of keep) {
    const card = parseClass(classNames[k.cls] || "");
    if (card) detections.push({ card, box: k.box, conf: k.score });
  }
  return detections;
}

// ---------- app ----------
const video = document.getElementById("video");
const overlay = document.getElementById("overlay");
const octx = overlay.getContext("2d");
const el = id => document.getElementById(id);

const tracker = new Tracker();
let session = new Session(6);
let rules = { decks: 6, h17: true, das: true, ls: false };
let zoneSplit = 0.45;
let statusUntil = 0;
let emptyStreak = 0, hadCards = false;
let newShoeArmedUntil = 0;

function flash(msg, seconds = 2.5) {
  el("status").textContent = msg;
  statusUntil = performance.now() + seconds * 1000;
}

function readRules() {
  rules = {
    decks: parseInt(el("rule-decks").value, 10),
    h17: el("rule-h17").value === "hit",
    das: el("rule-das").value === "yes",
    ls: el("rule-ls").value === "yes",
  };
  session = new Session(rules.decks);
  tracker.reset();
  flash("rules changed — new shoe");
}

function cardsOf(counts, zone) {
  const out = [];
  for (const [key, n] of counts) {
    const [cardId, z] = key.split("|");
    if (z !== zone) continue;
    const card = parseClass(cardId);
    for (let i = 0; i < n; i++) out.push(card);
  }
  out.sort((a, b) => a.id.localeCompare(b.id));
  return out;
}

function render(detections, counts) {
  const w = video.videoWidth, h = video.videoHeight;
  // pin the overlay exactly onto the video element (it centers in its flex
  // wrapper, so the canvas must follow its offset, not sit at the corner)
  overlay.style.left = video.offsetLeft + "px";
  overlay.style.top = video.offsetTop + "px";
  overlay.width = video.clientWidth; overlay.height = video.clientHeight;
  const sx = overlay.width / w, sy = overlay.height / h;
  octx.clearRect(0, 0, overlay.width, overlay.height);
  // zone line
  const ly = zoneSplit * h * sy;
  octx.strokeStyle = "#e6be5a"; octx.lineWidth = 2;
  octx.beginPath(); octx.moveTo(0, ly); octx.lineTo(overlay.width, ly); octx.stroke();
  octx.fillStyle = "#e6be5a"; octx.font = "14px system-ui";
  octx.fillText("DEALER", 8, ly - 8); octx.fillText("PLAYER", 8, ly + 18);
  // boxes: one labeled box per card
  const strongest = new Map();
  for (const d of detections) {
    const zone = boxCenter(d.box)[1] < zoneSplit * h ? "D" : "P";
    const key = d.card.id + "|" + zone;
    if (!strongest.has(key) || d.conf > strongest.get(key).conf) strongest.set(key, d);
  }
  octx.strokeStyle = "#50dc78"; octx.fillStyle = "#50dc78";
  for (const d of detections) {
    const [x1, y1, x2, y2] = d.box;
    const zone = boxCenter(d.box)[1] < zoneSplit * h ? "D" : "P";
    const labeled = strongest.get(d.card.id + "|" + zone) === d;
    octx.lineWidth = labeled ? 2 : 1;
    octx.strokeRect(x1 * sx, y1 * sy, (x2 - x1) * sx, (y2 - y1) * sy);
    if (labeled) octx.fillText(d.card.id, x1 * sx, Math.max(y1 * sy - 5, 12));
  }
  // panel
  const dealer = cardsOf(counts, "D"), player = cardsOf(counts, "P");
  el("dealer-cards").textContent = dealer.map(c => c.id).join(" ") || "—";
  el("player-cards").textContent = player.map(c => c.id).join(" ") || "—";
  let action = "…";
  if (player.length >= 2 && dealer.length === 1) {
    action = decide(player, dealer[0], rules);
    el("player-total").textContent =
      `(${handValue(player).soft ? "soft" : "hard"} ${handValue(player).total})`;
  } else el("player-total").textContent = "";
  const actionEl = el("action");
  actionEl.textContent = action;
  actionEl.className = action.replace("!", "");
  const rc = session.running;
  el("running").textContent = (rc >= 0 ? "+" : "") + rc;
  el("true").textContent = (session.trueCount >= 0 ? "+" : "") + session.trueCount.toFixed(1);
  el("decks-left").textContent = session.decksRemaining.toFixed(1);
  el("bet").textContent = session.betUnits + "u";
  if (performance.now() > statusUntil) el("status").textContent = "";
}

function autoRound(counts) {
  const total = [...counts.values()].reduce((a, b) => a + b, 0);
  if (total > 0) { hadCards = true; emptyStreak = 0; return; }
  if (!hadCards) return;
  if (++emptyStreak >= 25) {
    session.endHand(); hadCards = false; emptyStreak = 0;
    flash(`hand #${session.hands} banked`);
  }
}

async function loop() {
  if (video.readyState >= 2 && video.videoWidth) {
    const t0 = performance.now();
    mergeFloor = MERGE_DIST * video.videoWidth / 1280;
    const detections = await detect(video, video.videoWidth, video.videoHeight);
    const { counts, events } = tracker.update(
      detections, zoneSplit * video.videoHeight, rules.decks);
    session.applyEvents(events);
    autoRound(counts);
    render(detections, counts);
    el("perf").textContent =
      `${video.videoWidth}×${video.videoHeight} · ${Math.round(performance.now() - t0)} ms/frame`;
  }
  requestAnimationFrame(loop);
}

async function startCamera(deviceId) {
  const constraints = {
    video: deviceId ? { deviceId: { exact: deviceId } }
                    : { facingMode: "environment", width: { ideal: 1280 } },
  };
  const stream = await navigator.mediaDevices.getUserMedia(constraints);
  video.srcObject = stream;
  await video.play();
  const devices = (await navigator.mediaDevices.enumerateDevices())
    .filter(d => d.kind === "videoinput");
  const sel = el("camera-select");
  sel.innerHTML = "";
  devices.forEach((d, i) => {
    const o = document.createElement("option");
    o.value = d.deviceId; o.textContent = d.label || `camera ${i + 1}`;
    sel.appendChild(o);
  });
}

async function main() {
  el("end-hand").onclick = () => { session.endHand(); flash(`hand #${session.hands} banked`); };
  el("new-shoe").onclick = () => {
    if (performance.now() < newShoeArmedUntil) {
      session.newShoe(); tracker.reset(); flash("new shoe — count reset");
      newShoeArmedUntil = 0;
    } else {
      newShoeArmedUntil = performance.now() + 2500;
      flash("press again to confirm new shoe");
    }
  };
  el("zone-slider").oninput = e => { zoneSplit = e.target.value / 100; };
  ["rule-decks", "rule-h17", "rule-das", "rule-ls"].forEach(id => {
    el(id).onchange = readRules;
  });
  el("camera-select").onchange = e => startCamera(e.target.value);

  try {
    await loadModel();
  } catch (e) {
    el("loading").textContent = "model failed to load: " + e.message;
    return;
  }
  try {
    await startCamera();
  } catch (e) {
    el("loading").textContent = "camera unavailable: " + e.message +
      " — allow camera access and reload";
    return;
  }
  el("loading").classList.add("hidden");
  loop();
}

main();
