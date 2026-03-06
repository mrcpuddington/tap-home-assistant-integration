from __future__ import annotations

from typing import Any

from homeassistant import config_entries
from homeassistant.helpers import config_entry_oauth2_flow
from homeassistant.helpers.config_entry_oauth2_flow import LocalOAuth2Implementation

from .const import (
    CONF_API_BASE_URL,
    CONF_CLIENT_ID,
    CONF_COGNITO_DOMAIN,
    CONF_SCOPES,
    DOMAIN,
    PROD_API_BASE_URL,
    PROD_CLIENT_ID,
    PROD_COGNITO_DOMAIN,
    PROD_SCOPES,
)


@config_entries.HANDLERS.register(DOMAIN)
class TapOAuth2FlowHandler(config_entry_oauth2_flow.AbstractOAuth2FlowHandler):
    VERSION = 1
    _oauth_config: dict[str, str]

    def __init__(self) -> None:
        super().__init__()
        self._oauth_config = {}

    @property
    def extra_authorize_data(self) -> dict[str, Any]:
        return {"scope": self._oauth_config.get(CONF_SCOPES, PROD_SCOPES)}

    def _apply_production_config(self) -> None:
        self._oauth_config = {
            CONF_API_BASE_URL: PROD_API_BASE_URL.rstrip("/"),
            CONF_COGNITO_DOMAIN: PROD_COGNITO_DOMAIN.rstrip("/"),
            CONF_CLIENT_ID: PROD_CLIENT_ID,
            CONF_SCOPES: PROD_SCOPES,
        }
        self.flow_impl = LocalOAuth2Implementation(
            self.hass,
            DOMAIN,
            self._oauth_config[CONF_CLIENT_ID],
            "",
            f"{self._oauth_config[CONF_COGNITO_DOMAIN]}/oauth2/authorize",
            f"{self._oauth_config[CONF_COGNITO_DOMAIN]}/oauth2/token",
        )

    async def async_step_user(
        self, user_input: dict[str, str] | None = None
    ) -> config_entries.ConfigFlowResult:
        self._apply_production_config()
        return await self.async_step_auth()

    async def async_oauth_create_entry(self, data: dict[str, Any]) -> config_entries.ConfigFlowResult:
        title = "Tap"
        return self.async_create_entry(
            title=title,
            data={
                **self._oauth_config,
                **data,
            },
        )

    async def async_step_reauth(self, user_input: dict[str, Any] | None = None) -> config_entries.ConfigFlowResult:
        self._apply_production_config()
        return await super().async_step_reauth(user_input)
