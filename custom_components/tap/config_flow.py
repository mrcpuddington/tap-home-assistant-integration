from __future__ import annotations

from typing import Any
import logging

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

_LOGGER = logging.getLogger(__name__)


class TapOAuth2FlowHandler(config_entry_oauth2_flow.AbstractOAuth2FlowHandler, domain=DOMAIN):
    DOMAIN = DOMAIN
    VERSION = 1
    _oauth_config: dict[str, str]

    def __init__(self) -> None:
        super().__init__()
        self._oauth_config = {}

    @property
    def logger(self) -> logging.Logger:
        return _LOGGER

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

    def _build_local_implementation(self) -> LocalOAuth2Implementation:
        return LocalOAuth2Implementation(
            hass=self.hass,
            domain=DOMAIN,
            client_id=self._oauth_config[CONF_CLIENT_ID],
            client_secret="",
            authorize_url=f"{self._oauth_config[CONF_COGNITO_DOMAIN]}/oauth2/authorize",
            token_url=f"{self._oauth_config[CONF_COGNITO_DOMAIN]}/oauth2/token",
        )

    async def _start_oauth_flow(self) -> config_entries.ConfigFlowResult:
        implementation = self._build_local_implementation()
        register_local_impl = getattr(self, "register_local_implementation", None)
        if callable(register_local_impl):
            register_local_impl(self.hass, implementation)
            pick_impl = getattr(self, "async_step_pick_implementation", None)
            if callable(pick_impl):
                return await pick_impl()

        # Backward-compatible path for HA versions that rely on flow_impl/async_step_auth.
        self.flow_impl = implementation
        return await self.async_step_auth()

    async def async_step_user(
        self, user_input: dict[str, str] | None = None
    ) -> config_entries.ConfigFlowResult:
        try:
            self._apply_production_config()
            return await self._start_oauth_flow()
        except Exception:  # noqa: BLE001
            _LOGGER.exception("Failed to initialize Tap OAuth flow")
            return self.async_abort(reason="oauth_init_failed")

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
        try:
            self._apply_production_config()
            implementation = self._build_local_implementation()
            register_local_impl = getattr(self, "register_local_implementation", None)
            if callable(register_local_impl):
                register_local_impl(self.hass, implementation)
            else:
                self.flow_impl = implementation
            return await super().async_step_reauth(user_input)
        except Exception:  # noqa: BLE001
            _LOGGER.exception("Failed to initialize Tap OAuth reauth flow")
            return self.async_abort(reason="reauth_failed")
