# Tap Home Assistant Integration

Home Assistant custom integration for Tap cloud sync.

## Features (v1)

- Summary sensors for tasks/events/logs.
- Per-task sensors with status + recent completion history.
- Per-event sensors with metadata.
- Per-log sensors with recent entries.
- Services:
  - `tap.complete_task`
  - `tap.reopen_task`
  - `tap.add_log_entry`

## Install (HACS)

1. Open HACS -> Integrations -> Custom repositories.
2. Add this repository as `Integration`.
3. Install `Tap`.
4. Restart Home Assistant.
5. Add integration from Settings -> Devices & Services.

## Install (Manual ZIP)

1. Download the latest release ZIP.
2. Copy `custom_components/tap` into your Home Assistant `custom_components` directory.
3. Restart Home Assistant.
4. Add integration from Settings -> Devices & Services.

## Setup

Production OAuth/API settings are preconfigured in the integration.

You only need to:

1. Add the integration.
2. Click connect/sign in.
3. Complete OAuth login.

## Notes

- This integration uses OAuth2 Authorization Code + PKCE.
- All cloud reads/writes are owner-scoped by Cognito `sub`.
- Supported write actions in v1 are intentionally limited for safety.
