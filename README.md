# Video-Creation (master)

Master repo for the owner's projects. It links each repo as a pinned git submodule, vendors one reel kit, and runs liaison agents that operate each repo and pass work to each other through a handoff queue.

```
scripts/bootstrap.sh                      # fetch the submodules
python3 tools/master.py status            # what is installed / synced
python3 tools/master.py route "<task>"    # which repo and agent
python3 -m unittest discover -s tests
```
In Claude Code: `/master <task>`. Rules: `AGENTS.md`. Registry: `master.json`. Design: `docs/ARCHITECTURE.md`.
