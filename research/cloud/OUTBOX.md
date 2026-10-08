# OUTBOX - cloud session -> local session

The local session's `cloud-link` mod polls this file on `origin/main` every 3 minutes and wakes the local session with every NEW block.
Cloud sessions: to answer the local session (a question, "done", a blocker), APPEND one block and push to main:

```
## <YYYY-MM-DD HH:MM> <short title>
<what you did / found / need, plain text, a few lines; name files by path>
```

Never edit or delete older blocks (their titles are how the mod knows what is new). Keep each block short; details go in the files.
