# Marcus Access Boundaries

## Read

- Entire project workspace
- Runtime state under `state/`
- Other sidecars as read-only context when needed

## Write

- `_bmad/memory/bmad-agent-marcus-sidecar/`
- Approved run outputs and runtime state through canonical workflow paths

## Deny

- `.env`
- Other agents' sidecars
- Unapproved production artifacts outside the active workflow
