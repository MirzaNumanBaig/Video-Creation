#!/usr/bin/env bash
# Copy the Instagram and YouTube skills from the pinned submodules into .claude/skills/
# (project-local skills must be real files). Re-run after moving a submodule pin.
set -eu
cd "$(dirname "$0")/.."
python3 tools/master.py sync instagram-agent-skill youtube-agent-skill paper-reel explainroo remotion-skills
mkdir -p .claude/skills
for d in repos/instagram-agent-skill/skills/ig-* repos/youtube-agent-skill/skills/yt-*; do
  [ -f "$d/SKILL.md" ] || continue
  rm -rf ".claude/skills/$(basename "$d")"
  cp -r "$d" ".claude/skills/$(basename "$d")"
done
# Video skills stay inside their pinned submodules and are linked in (no copies).
link(){ rm -rf ".claude/skills/$1"; ln -s "$2" ".claude/skills/$1"; }
link paper-reel ../../repos/paper-reel
link explainroo ../../repos/explainroo/skills/explainroo
link remotion-best-practices ../../repos/remotion-skills/skills/remotion-best-practices
link subtle ../../repos/subtle
find .claude/skills -name __pycache__ -prune -exec rm -rf {} +
ls .claude/skills | tr '\n' ' '; echo
