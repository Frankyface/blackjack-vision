# /verify — run the verification loop on the active feature

Target: the active feature file named in `handoff.md`'s **🔗 Pointer** (or the feature Cam
names explicitly).

1. **Claim** — state what you believe is complete and which of the feature's Success Criteria
   it satisfies.
2. **Test** — actually execute the feature's **How We'll Verify** procedure: run the commands,
   exercise the behavior end-to-end the way a real user would. "It compiles", "the code looks
   right", and "the tests I just wrote pass" do not count on their own. If a step needs Cam
   (live table, webcam pointing at cards, the Pi), ask him to do it now or mark it blocked.
3. **Evidence** — append a dated entry to the feature's **Verification Log**: what was run, the
   real output/result, including failures.
4. **Status** — per the state machine `not started → in progress → awaiting verification →
   verified done`:
   - Pass → `verified done`; tick the satisfied Success Criteria; sync the stage `overview.md`
     feature checklist.
   - Fail → stays `in progress`; record the failure; if it was a dead end, append it to
     `docs/failed-approaches.md`.
   - Blocked (missing hardware/account/Cam) → stays `awaiting verification`; add the blocker
     to `help.md`; tell Cam. **Never silently mark it done.**

Never weaken Success Criteria to make them pass — changing criteria needs Cam's explicit
sign-off plus a `docs/decisions.md` entry.

Minimum bar for ANY coding task, even outside a feature file: (1) runs without errors,
(2) automated tests pass — write at least a smoke test if none exist, (3) the behavior is
exercised end-to-end. All three, or it isn't done.
