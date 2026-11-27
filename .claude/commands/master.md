---
description: Master entry point: take a task, route it to the right liaison agent(s), run them, report
---
Task from the owner: $ARGUMENTS

You are the master orchestrator (see AGENTS.md). Do this:
1. `python3 tools/master.py status` — note repos that are not synced; sync only what the task needs.
2. `python3 tools/master.py route "$ARGUMENTS"` — pick the liaison agent(s). If it spans repos, write a short plan (who does what, in what order, what passes between them) and show it before running anything outward-facing.
3. Run independent liaisons in parallel (separate Agent calls in one message); dependent steps in order. Pass work between agents with `handoff new`, not by pasting content.
4. Anything that publishes, merges, posts, sends or spends goes through `release-gate` and the owner first.
5. Reply: what needs the owner first, then what was done, then open handoffs. Keep it short.
