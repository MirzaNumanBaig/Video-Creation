#!/usr/bin/env bash
# Copy the Instagram and YouTube skills from the pinned submodules into .claude/skills/
# (project-local skills must be real files). Re-run after moving a submodule pin.
set -eu
cd "$(dirname "$0")/.."
python3 tools/master.py sync instagram-agent-skill youtube-agent-skill
mkdir -p .claude/skills
for d in repos/instagram-agent-skill/skills/ig-* repos/youtube-agent-skill/skills/yt-*; do
  [ -f "$d/SKILL.md" ] || continue
  rm -rf ".claude/skills/$(basename "$d")"
  cp -r "$d" ".claude/skills/$(basename "$d")"
done
find .claude/skills -name __pycache__ -prune -exec rm -rf {} +
ls .claude/skills | tr '\n' ' '; echo
