# Final Report Notes

Use these exact edits in the final PDF/report.

Replace "136 unit tests across five test files" with:

"136 unit tests across six test files."

Replace "Five test files were written..." with:

"Six test files were written: test_cli.py, test_data.py, test_game_engine.py, test_main.py, test_models.py, and test_validation.py."

Replace the pdoc section wording with:

"Formal HTML documentation was generated using pdoc and committed to the repository under docs/pdoc.
Command run:
pdoc cli.py data.py game_engine.py validation.py models.py main.py -o docs/pdoc
Output location:
docs/pdoc/index.html"

Coverage report paths:

- `docs/coverage/unit/index.html`
- `docs/coverage/manual/index.html`
- `docs/coverage/combined/index.html`

Requirements Coverage:

"Each of the 32 individual NLRs (NLR-1.1 through NLR-10.3) is mapped to manual and unit tests."

Postmortem should include:

- Earned Value
- Variances
- Lessons Learned
- Future Maintenance
- Team Reflection
