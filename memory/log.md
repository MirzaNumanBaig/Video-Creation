# Master log

One line per action: `- <date> · <agent> · <what> · <result>`

- 2026-11-27 · master · Created registry, 10 liaison agents, CLI and handoff queue; linked 10 repos + 1 vendored kit · see docs/ARCHITECTURE.md
- 2026-11-27 · master · Installed 13 ig-* and 11 yt-* skills into .claude/skills via scripts/install-skills.sh · hookscore smoke test OK
- 2026-11-27 · video-liaison · reel-studio-kit: npm install, typecheck OK, demo rendered 1080x1920 15.2s (BROWSER_EXECUTABLE=/opt/pw-browsers/chromium) · caption sync (Whisper) and voice not yet set up
- 2026-11-27 · video-liaison · Added free Piper voice provider + Whisper captions to reel-studio-kit; demo rendered with real voice (13.7s, h264+aac), self-check clean, contact sheet viewed · no paid APIs per owner
- 2026-11-27 · video-liaison · Vendored remotion-captioneer styles (14 styles, 23 presets, MIT) into reel-studio-kit/src/captioneer + StyledCaptions + CaptionGallery; demo variants Cap-TikTok/Cap-Bounce rendered, self-check clean, contact sheet viewed
