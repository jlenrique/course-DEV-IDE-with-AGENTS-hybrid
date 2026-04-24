# bmad-create-specialist

Generate a scaffold-conformant specialist package and its lockstep test/fixture
files.

## Command

```bash
python -m skills.bmad_create_specialist.scripts.generate \
  --name <specialist_name> \
  --mcp <none|gamma|elevenlabs|canvas|kling|wondercraft> \
  --expertise-tier <L3-... through L7-...> \
  [--from-skill skills/bmad-agent-<name>/] \
  [--dry-run] \
  [--force]
```

## Arguments

- `--name`: required; regex `^[a-z][a-z0-9_]*$`.
- `--mcp`: required enum; MCP tool hint.
- `--expertise-tier`: required; regex `^L[3-7]-[a-z0-9-]+$`.
- `--from-skill`: optional source skill directory under `skills/bmad-agent-*/`.
- `--dry-run`: validate and print deterministic planned writes, no filesystem writes.
- `--force`: overwrite existing generated files.

## Guarantees

- Unknown template vars are preserved literally (`{{unknown_var}}` survives).
- Named failures surface as `GeneratorInputError: <reason>`.
- Dry-run validates parse/shape gates and exits with wet-run-equivalent status.
- Emission is atomic for targeted files (rollback on partial-write failure).
- Category D denylist is enforced for `--from-skill`:
  - `bmad-agent-audra`
  - `bmad-agent-cora`

## Outputs

- `app/specialists/<name>/...` scaffold package.
- `tests/specialists/<name>/test_<name>_state_shape.py`.
- `tests/fixtures/specialists/<name>/golden_envelope.json`.
- `tests/fixtures/specialists/<name>/golden_return.json`.
- `tests/integration/scaffold_conformance/test_scaffold_<name>.py`.
