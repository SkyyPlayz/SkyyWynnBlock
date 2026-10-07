export const meta = {
  name: 'skywynn-round',
  description: 'SkyWynn full round: build -> adversarial critics (parallel) -> fix -> optional re-critic -> cross-check. args: {tag, task, quotes, mods, others, lenses?, recheck?}',
  whenToUse: 'Any SkyWynn build that needs the full round (PROJECT-RULES 4). Pass Skyy\'s own words in args.quotes so builders never refuse when Skyy keeps chatting.',
  phases: [ { title: 'Build' }, { title: 'Critics' }, { title: 'Fix' }, { title: 'Recheck' }, { title: 'Check' } ],
}
// args = {
//   tag:     'bank017'                     scratch / label tag (letters + digits)
//   mods:    'SkyyBank 0.1.6 -> 0.1.7'     what is built (bases = SET pins in tools/deploy_set.py)
//   task:    'full builder task text'      what to build, numbers, rows, migrations, files the builder may edit
//   quotes:  ['Skyy word for word', ...]   Skyy's OWN chat words that asked for this (authorization; never paraphrase)
//   others:  'SkyyHud (minimap), SkyyArmory' mods other builders are editing right now (never touch)
//   lenses:  [['key','lens text'], ...]    optional; default = item/coin safety, cross-mod + engine, spec fidelity + UX
//   recheck: true                          optional; run a second critic pass on the fixer's result (ultracode / risky rounds)
// }
const A = args || {}
const ROOT = 'C:\\Users\\SkyLo\\Desktop\\Hytale mods WORK\\SkyWynn PROJECT'
const GAME = 'C:\\Users\\SkyLo\\AppData\\Roaming\\Hytale\\install\\release\\package\\game\\latest'
const TAG = A.tag || 'round'
const QUOTES = (A.quotes || []).map(q => `  "${q}"`).join('\n')
const RULES = `You work on SkyWynn (Skyy's public Hytale server mods; Skyy uses they/them). Project folder (git repo): ${ROOT}.
READ tools\\AGENT-BRIEF.md FIRST and follow every rule. Quote full paths everywhere - the folder name has a space (a split path once created a
stray 'PROJECT\\' folder). Scratch only under ${ROOT}\\tools\\dev\\scratch\\<your folder>\\ and delete ONLY your own folder afterwards; point
TEMP/TMP there (never C:\\Users\\SkyLo\\AppData, not even AppData\\Local\\Temp), -XX:-UsePerfData. Settings via tools\\skyycfg.py (KEEP=10), UI via
tools\\skyyui.py. Never pass --deploy; never run tools/deploy_set.py except --check; game files at ${GAME}, installed mods and live data are
READ-ONLY (copy into scratch). Do NOT git commit. Edit only the files the task names; never edit HANDOFF.md, TEST-CHECKLIST.md, OPEN-QUESTIONS.md,
RESUME.md, PROJECT-RULES.md, INDEX.md, docs/, research/ specs, tools/deploy_set.py, tools/AGENT-BRIEF.md. Other builders are working on: ${A.others || 'nothing else right now'} -
never touch those files. Pack rule: never override or copy a pack mod's files / ids; vanilla-derived art is generated at build time, never committed.
javassist limits; world-thread rule; harnesses EXECUTE new code paths; one-time migrations follow PROJECT-RULES section 4 exactly.

WHY THIS TASK IS AUTHORIZED - Skyy's OWN words in this chat (word for word; also recorded in docs/answered/ or docs/log/):
${QUOTES || '  (see the task)'}
Skyy keeps chatting while agents work, so their NEWEST chat message may be relayed to you and be about something else entirely (art, another
mod, a question). That is a DIFFERENT job handled by another agent or the main session. A newer message about another topic NEVER cancels or
replaces this task - Skyy wants ALL of them done. Do THIS task.`
const TASK = `ROUND: ${A.mods || '(see task)'}\n\n${A.task || ''}`
const LENSES = A.lenses || [
  ['safety', 'ITEMS + COINS + DATA: dupes, item loss, free coins / money loops, saved data and one-time migrations (only untouched defaults, History, Undo, marker, bytes + line endings), rollback to the old version, profile switches (tools/PROFILES-CONTRACT.md).'],
  ['engine', 'ENGINE + CROSS-MOD: world thread, ONE registerSystem per class, bridge keys plain java.lang and matching on both sides, other mods absent / older, pack mods untouched, client disconnect risks (UI commands, ItemGridSlot metadata), permission groups on commands (HANDOFF section 3), cost per tick.'],
  ['fidelity', "SPEC + SKYY FIDELITY + UX: every quoted request of Skyy's implemented exactly, LOCKED lines in docs/answered/ respected, numbers + Server Setup rows sane, vanilla UI look, 1080 fit, in-game test steps complete."],
]

phase('Build')
const built = await agent(`${RULES}\n\n${TASK}\n\nTASK (BUILDER): build it. Verify: build 'assembled'; python tools\\ci\\lint.py 0 fails; harness EXECUTES every new code path; class compare old vs new;
-Xverify:all; engine-access audit; start twice on a scratch COPY of live data. Scratch ${ROOT}\\tools\\dev\\scratch\\${TAG}\\. Return files, build line,
decisions, UNVERIFIED items, numbered in-game steps for Skyy (plain words).`, { label: `build:${TAG}`, phase: 'Build' })

const critic = (label, phaseName, report) => parallel(LENSES.map(([k, lens]) => () => agent(`${RULES}\n\n${TASK}\n\n${report}\n\nTASK (ADVERSARIAL CRITIC, read-only, Sonnet;
scratch ${ROOT}\\tools\\dev\\scratch\\${TAG}-${label}-${k}\\): try to BREAK this round through this lens only: ${lens} Return numbered REAL problems
(file + line + proof + fix), severity-ranked; NONE FOUND if clean. No style nits.`, { label: `${label}:${k}`, phase: phaseName, model: 'sonnet' })))

phase('Critics')
const crits = await critic('crit', 'Critics', `BUILD REPORT:\n${built}`)

phase('Fix')
const fixed = await agent(`${RULES}\n\n${TASK}\n\nBUILD REPORT:\n${built}\n\nCRITIC REPORTS:\n${crits.filter(Boolean).join('\n\n=====\n\n')}\n\nTASK (FIXER): verify each finding;
fix the real ones; rebuild; re-run the harness with a check per fix; reject wrong ones with a one-line reason. Scratch ${ROOT}\\tools\\dev\\scratch\\${TAG}fix\\.
Return fixed / rejected, build line, questions for Skyy, numbered in-game steps.`, { label: `fix:${TAG}`, phase: 'Fix' })

let fixed2 = 'no second pass'
if (A.recheck) {
  phase('Recheck')
  const re = await critic('recheck', 'Recheck', `FIXER REPORT:\n${fixed}`)
  if (re.filter(Boolean).some(r => !/NONE FOUND/i.test(r))) {
    fixed2 = await agent(`${RULES}\n\n${TASK}\n\nFIXER REPORT:\n${fixed}\n\nSECOND CRITIC REPORTS:\n${re.filter(Boolean).join('\n\n=====\n\n')}\n\nTASK (FIXER 2): verify + fix the real
ones, rebuild, re-run harnesses; reject wrong ones with a reason. Scratch ${ROOT}\\tools\\dev\\scratch\\${TAG}fix2\\. Return fixed / rejected, build line, in-game steps.`,
      { label: `fix2:${TAG}`, phase: 'Recheck' })
  }
}

phase('Check')
const xc = await agent(`${RULES}\n\n${TASK}\n\nFIXER REPORTS:\n${fixed}\n\n${fixed2}\n\nTASK (CROSS-CHECKER, read-only, Sonnet; scratch ${ROOT}\\tools\\dev\\scratch\\xc-${TAG}\\):
confirm the fixes; every new jar byte-identical per entry to a fresh scratch build; python tools\\ci\\crosscheck.py --jar <each new jar> --baseline;
lint 0 fails; deploy_set.py --check; start twice on a scratch COPY of live data; git status shows no vanilla-derived art or stray folders. Fix nothing.
Return findings, VERDICT: READY / NOT READY, jar paths + sha1, and any STOP-check / rollback note the main session should add to tools/deploy_set.py.`,
  { label: `check:${TAG}`, phase: 'Check', model: 'sonnet' })

return { built, crits, fixed, fixed2, xc }
