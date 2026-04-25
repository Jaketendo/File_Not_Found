# Release 2 - Final Verification and Repository Cleanup

Branch: `release-2`

Latest commit hash at note generation: `f74f687`

## Summary

Release 2 fixes the circular import that prevented `main.py` from running,
restores `game_engine.py` as a source module, organizes active tests under
`tests/`, adds focused model tests, removes duplicate root-level generated files,
and commits the professor-facing evidence artifacts under `docs/`.

## Features Included

- Working command-line game startup through `main.py`.
- Restored game engine source with search, unlock, evidence, and submission APIs.
- Six active automated test files under `tests/`.
- Manual/integration verification script covering MT-01 through MT-04.
- pdoc HTML documentation under `docs/pdoc`.
- Unit, manual, and combined coverage HTML reports under `docs/coverage`.
- Git history evidence under `docs/git/git_log.txt`.

## Verification Status

- `python main.py` starts without import errors.
- `python -m pytest -q tests` reports 136 passing tests.
- pdoc documentation was regenerated for the six source modules.
- Unit, manual, and combined coverage reports were generated.

## Evidence Paths

- `docs/testing/test-results.txt`
- `docs/testing/test-inventory.txt`
- `docs/pdoc/index.html`
- `docs/coverage/unit/index.html`
- `docs/coverage/manual/index.html`
- `docs/coverage/combined/index.html`
- `docs/git/git_log.txt`
