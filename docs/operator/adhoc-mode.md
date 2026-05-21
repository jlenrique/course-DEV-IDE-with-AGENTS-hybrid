# Marcus Ad-hoc Mode

Ad-hoc mode is the single-prompt runtime path for asking Marcus a question without opening or registering a tracked trial.

```bash
.venv/Scripts/python.exe -m app.marcus.cli ask "What would change if this lesson used a case-study structure?"
```

Use it for exploration, quick summaries, trial planning questions, and operator-side prompt templates. It does not run the production pipeline, trigger HIL gates, write `state/config/runs/`, mutate sanctum, or append to a trial cost report.

## Options

- `--cascade-override marcus=<model>`: one invocation only. This does not edit `runtime/config/model_cascade.yaml`.
- `--max-tokens <N>`: cap the response length.
- `--no-trace`: skip LangSmith tracing.
- `--json`: emit machine-readable output.

Default traces go to the LangSmith project `course-content-adhoc` so exploratory runs stay separate from `course-content-production`.

Cost is printed inline. Plain-text mode writes Marcus's answer to stdout and a one-line cost summary to stderr; JSON mode includes `response.cost_usd`, `response.model_used`, and token counts.
