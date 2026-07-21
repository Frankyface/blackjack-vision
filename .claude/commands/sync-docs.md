# /sync-docs — update all relevant files

Trigger: Cam says "update all relevant files" or runs `/sync-docs`.

1. **Review what actually happened this session** — what changed, what was decided, what got
   built, what failed. Record reality only: nothing unverified gets written down as working.

2. **Update, as needed:**
   - `handoff.md` — ALWAYS. Rewrite every section in place (🎯 Goals, 📍 Current State,
     📂 Files, ✅ Changed, ❌ Watch Out, ➡️ Next Up, 🔗 Pointer). Enforce the budget:
     ≤ 60 lines total; "Changed" keeps only the last 5 entries (older ones DELETED — git log
     is the archive); "Watch Out" at most 3 one-liners, each linking into
     `docs/failed-approaches.md`. Over budget → compressing it is part of the sync.
   - Active **feature files** in `staging/` — Status per the /verify state machine
     (`verified done` requires a Verification Log entry, no exceptions); resolve or append
     Open Questions.
   - Stage **overview.md** — if scope/done-criteria shifted or a feature's checkbox flipped.
   - `docs/decisions.md` — APPEND any decision made this session (chose/because/rejected/
     revisit-if). Never rewrite old entries.
   - `docs/failed-approaches.md` — APPEND any dead end (root cause + do-instead).
   - `docs/master_plan.md` — only if the vision/roadmap genuinely changed.
   - `CLAUDE.md` — only if a rule, convention, or stack fact changed.
   - `new_session_prompt.md` / `.claude/commands/resume.md` — if resume instructions changed.
   - `help.md` — new human to-dos appeared or old ones completed.

3. **Infer relevance from the session** — don't quiz Cam with a checklist; decide what changed
   and update those files.

4. **Integrity check:** handoff.md's Pointer resolves to a real stage folder + feature file;
   handoff.md is within its 60-line budget; every `verified done` feature has Verification Log
   evidence; no file left mid-edit.

5. **Report back in 3–5 lines:** which files were updated and why, plus anything deliberately
   NOT updated.

6. Offer to commit: `docs: sync session state`.
