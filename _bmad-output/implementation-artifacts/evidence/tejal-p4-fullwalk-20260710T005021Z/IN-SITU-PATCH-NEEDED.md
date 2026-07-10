# In-situ patch needed mid-walk

```json
{
  "tag": "irene.pass2.figure-contradiction",
  "detail": "05021Z\\tejal_p4_fullwalk_driver.py\", line 421, in maybe_recover\n    payload = recover_trial(\n              ^^^^^^^^^^^^^^\n  File \"C:\\Users\\juanl\\Documents\\GitHub\\course-DEV-IDE-with-AGENTS-hybrid\\app\\marcus\\cli\\trial.py\", line 820, in recover_trial\n    envelope = recover_production_trial(\n               ^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"C:\\Users\\juanl\\Documents\\GitHub\\course-DEV-IDE-with-AGENTS-hybrid\\app\\marcus\\orchestrator\\production_runner.py\", line 3119, in recover_production_trial\n    return _continue_production_walk(\n           ^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"C:\\Users\\juanl\\Documents\\GitHub\\course-DEV-IDE-with-AGENTS-hybrid\\app\\marcus\\orchestrator\\production_runner.py\", line 3187, in _continue_production_walk\n    production_envelope = _apply_variant_selection(\n                          ^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"C:\\Users\\juanl\\Documents\\GitHub\\course-DEV-IDE-with-AGENTS-hybrid\\app\\marcus\\orchestrator\\production_runner.py\", line 1193, in _apply_variant_selection\n    return _apply_per_slide_variant_selection(production_envelope, run_state)\n           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"C:\\Users\\juanl\\Documents\\GitHub\\course-DEV-IDE-with-AGENTS-hybrid\\app\\marcus\\orchestrator\\production_runner.py\", line 1139, in _apply_per_slide_variant_selection\n    raise VariantSelectionError(\napp.marcus.orchestrator.production_runner.VariantSelectionError: per-slide variant selection is set, but latest Gary output has no gary_slide_output\n",
  "known_good": {
    "gate": "G2C",
    "at": "2026-07-10T04:59:20.619557+00:00"
  },
  "at": "2026-07-10T05:09:57.120111+00:00"
}
```

Policy: quick-dev patch → recover to known-good → continue.
