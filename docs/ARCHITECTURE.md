# Architecture

## Why submodules, not copies
The linked repos run live automation (xplorekit-dashboard every 3 hours, researcher-agents collection and writing workflows, seo-desk routines) and hold thousands of generated files. A copy would be stale immediately and would fork the history. A submodule pins an exact commit of each repo and leaves the repo independent. `vendor/reel-studio-kit` is the one exception: it came as a zip with no upstream git, so it is vendored as plain files.

## Layout
```
master.json            registry: repos, flows, agents, rules (single source of truth)
AGENTS.md / CLAUDE.md  the master's rules and routing table
.claude/agents/        10 liaison agents (one per repo cluster + broker, gate, scout)
.claude/commands/      /master /status /route /handoff /sync-repos
tools/master.py        status, sync, route, handoff, validate (stdlib only)
handoffs/queue/        file-based messages between agents
memory/log.md          action log
repos/<name>           submodules (pinned commits)
vendor/reel-studio-kit vendored kit
tests/                 unit tests (python3 -m unittest discover -s tests)
```

## Repos
| Name | Kind | What | Operated by |
|---|---|---|---|
| seo-desk | private | SEO agent team, project: xplorekit | seo-liaison |
| content-creation-agency | private | SEO Engine, TS pipeline for client blogs | seo-engine-liaison |
| xplorekit | private | live directory site (Cloudflare) | directory-liaison |
| xplorekit-dashboard | public | 3-hourly research feed into xplorekit | directory-liaison |
| researcher-agents | public | AU celebrity news -> articles -> WordPress | news-content-liaison |
| clips-studio | public | clips from long video (fork of ColinGPT9/clips-studio) | video-liaison |
| reel-studio-kit | vendored | faceless reels from a topic (Remotion) | video-liaison |
| explainroo | public, third party | free narrated explainer videos (verified end to end here) | video-liaison |
| paper-reel | public, third party | cut-paper reels; macOS-oriented, not working on Linux yet | video-liaison |
| remotion-skills | public, third party | Remotion's official agent skills | video-liaison |
| pin-creator | public | product URL -> Pinterest pin | pinterest-liaison |
| instagram-agent-skill | public, third party | 13 Instagram skills | social-liaison |
| youtube-agent-skill | public, third party | 11 YouTube skills | social-liaison |
| ai-agents | public | README only | none |
| Modus-Carry, Sell-Birds-Runner, SEO-Audit-Tool | public | empty (no commits) | none |
| awesome-claude-video-skills | reference | third-party catalogue, not installed | none |

## Data flows
`live` flows exist today inside the repos; `proposed` flows are ideas the master can run on request and are not wired up.

```
xplorekit-dashboard --PR, auto-merge--> xplorekit            (live)
seo-desk --work branch + gate--> xplorekit                   (live)
researcher-agents --approved drafts--> WordPress             (live)
content-creation-agency --Herald, status pending--> WordPress (live)
seo-desk strategy --> content-creation-agency briefs         (proposed)
instagram-agent-skill script --> reel-studio-kit --> caption (proposed)
youtube-agent-skill yt-shorts --> clips-studio               (proposed)
researcher-agents article --> reel;  xplorekit page --> pin  (proposed)
```

## How agents emulate each other
No agent calls another directly. Each liaison runs its repo's own system and posts a handoff (`master.py handoff new`) naming the next agent and a `ref` path. The handoff-broker routes, the release-gate checks anything outward-facing, and `owner` is a valid recipient for decisions. This keeps every step resumable and auditable, the same pattern the seo-engine repo already uses (artifacts as the only channel).

## Setup on a new machine
```
git clone <this repo> && cd Video-Creation
scripts/bootstrap.sh            # submodules at pinned commits; private repos need your git login
python3 tools/master.py status
```
Then in Claude Code: `/master <task>`.

## Moving a pin
`git -C repos/<name> fetch && git -C repos/<name> checkout <sha>` then commit the new gitlink in this repo. Only on the owner's say-so.

## Open items for the owner
- Empty repos (Modus-Carry, Sell-Birds-Runner, SEO-Audit-Tool) and ai-agents: purpose?
- pin-creator: auto-post allowed, or approval each time?
- Reel kit voice is free: Piper (local TTS) + local Whisper captions, no API keys. Piper's `en_US-lessac-medium` is a clear but plain voice; other voices can be added with `npm run setup:voice -- <voice>`.
- Reel kit: Remotion's licence is paid for larger companies; confirm your size.
- Video skills linked from submodules into `.claude/skills/` (symlinks, run `scripts/install-skills.sh` after cloning): `explainroo`, `paper-reel`, `remotion-best-practices`.
- Skills: the 13 `ig-*` and 11 `yt-*` skills are installed project-local in `.claude/skills/` (copies of the pinned submodules; refresh with `scripts/install-skills.sh` after moving a pin). Each reads a voice profile you still need to create: `~/.claude/instagram/voice.md` and `~/.claude/youtube/voice.md` (templates in each repo's `templates/voice.md`).
- The reel kit's own skill (`reels`) loads when Claude runs inside `vendor/reel-studio-kit`; it needs `npm install` there first.
