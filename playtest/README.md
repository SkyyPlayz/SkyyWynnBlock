# Playtest videos

Skyy records a play session, Skyy's Grok bot watches it, and Claude reads Grok's notes. Nothing in `videos/` or `notes/` is committed
(big files that may show chat or names); only these READMEs and the checklist are public.

1. Drop the clip in `playtest/videos/` named `YYYY-MM-DD-<what>.mp4` (e.g. `2026-10-12-requip.mp4`).
2. Give Grok the clip + [GROK-CHECKLIST.md](GROK-CHECKLIST.md) (paste it in) + anything you said to look for.
3. Save Grok's answer as `playtest/notes/<same name>.md` (or paste it in chat) and tell Claude.
4. Claude also reads the in-game chat of that session from the server log (`python tools/chat_tail.py`) - no chat screenshots needed.
5. After Claude has read the notes, delete the video (Recycle Bin) so it doesn't fill the disk.

Backup when Grok is unavailable: `python tools/llm.py --video playtest/videos/<clip>.mp4 "<question>"` (Jev router, short clips <= 40 MB).
