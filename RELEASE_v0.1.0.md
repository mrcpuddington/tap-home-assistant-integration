## Tap Home Assistant Integration v0.1.0

### Included
- OAuth2 Authorization Code + PKCE connection flow.
- Production preset cloud config (no manual endpoint/client entry).
- Read entities:
  - summary sensors (tasks/events/logs)
  - per-task sensors with status/history attributes
  - per-event sensors with metadata attributes
  - per-log sensors with recent entries
- Services:
  - `tap.complete_task`
  - `tap.reopen_task`
  - `tap.add_log_entry`

### API Contract
- Uses `/ha/v2/*` endpoints.
- JWT owner scoping via Cognito `sub`.
- No create/delete/edit task/event/log operations in v1.

### Release Artifact
- `dist/tap-home-assistant-integration-v0.1.0.zip`
- SHA-256:
  - `d4dd905d6f4658cd86ff6c54c1a05ae91984890c31cd82ed226db4efa0a013fd`
