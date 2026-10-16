<!-- made by tools/make_readmes.py - edit that script, not this file -->
# tools/

Every script: build kits, patches, deploy, CI checks, art generators, contracts.

## Where things are
- Deploy path: `backup_deploy.py` -> `smoke_test.py` -> `deploy_set.py --yes` (the SET + rollback floors) -> `record_deploy.py` -> `tidy_local.py --yes`.
- Build kits: `skyybuild.py` (javassist via jpype), `skyyui.py` (UI), `skyycfg.py` (Server Setup), `skyymove.py`, `skyyart.py`.
- Patches: `<mod>_<ver>_patch.py` make the next version of a mod's build script. CI: `ci/lint.py`, `ci/crosscheck.py`, `ci/langdup.py`.
- Contracts for agents: `AGENT-BRIEF.md`, `CONFIG-CONTRACT.md`, `PROFILES-CONTRACT.md`, `CORE-CONTRACT.md`, `HUBS-CONTRACT.md`.
- Docs helpers: `qa_append.py` (record Skyy's answer + close the question), `docs_check.py`, `make_readmes.py` (these READMEs).
- Scratch: `tools/dev/scratch/<task>/` only (git-ignored), packed by `tidy_local.py --scratch <task>`.

## Where new things go
- A new patch: `tools/<mod>_<ver>_patch.py`. A new tool: here, plus one line in the `tools/` row of `INDEX.md`.

Map of the whole repo: `INDEX.md`. Rules: `PROJECT-RULES.md`.
