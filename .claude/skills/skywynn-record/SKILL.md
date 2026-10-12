---
name: skywynn-record
description: Record Skyy's answer / idea / decision word for word in docs/answered and queue it in RESUME, in one cheap step. Use every time Skyy states a design idea, answers a popup, or sets a rule.
---

# Record Skyy's words (one step)

- Skyy's words go in VERBATIM (typos and all) in quotes, then `->` the meaning in plain words. Popup answers: quote the picked label
  and any notes they typed.
- Topic file (docs/answered/<topic>.md): classes, gear, skills, mobs, world, economy, bags, ui, social, pets, project.
- Write the line(s) to `tools/dev/scratch/qa/x.txt` with a heredoc (`cat > ... <<'EOF'` - quoted EOF so apostrophes are safe), then:
  `python tools/qa_append.py <topic> tools/dev/scratch/qa/x.txt --no-question` (or `--close "<words of the open question>"`), `rm` it with a LITERAL path (an `rm $var/...` is blocked by the safety check).
- A rule for how we work -> also PROJECT-RULES.md (+ a memory note). A big idea -> `research/<Name>-Ideas.md` + an INDEX.md line.
  Work to build later -> one numbered line in RESUME.md "Next" (before "8. Specs waiting:").
- `python tools/docs_check.py` must say OK (a planned file named as a path = BROKEN: write it without the path).
- Commit ONLY those files (`git add <files>`), message `answers: <short>`, end with the Co-Authored-By line, `git pull --rebase
  --autostash`, push. Then reply to Skyy in a few lines.
- Big multi-line Python edits: write a script file with Write, then run it (a bash -c with nested quotes breaks).
