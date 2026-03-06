from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_entry_oauth2_flow
from homeassistant.helpers.config_entry_oauth2_flow import LocalOAuth2Implementation
from homeassistant.helpers.typing import ConfigType
import voluptuous as vol

from .api import TapApiClient
from .const import (
    ATTR_LOG_ID,
    ATTR_NOTE,
    ATTR_TASK_ID,
    CONF_API_BASE_URL,
    CONF_CLIENT_ID,
    CONF_COGNITO_DOMAIN,
    DATA_API,
    DATA_COORDINATOR,
    DOMAIN,
    PLATFORMS,
    SERVICE_ADD_LOG_ENTRY,
    SERVICE_COMPLETE_TASK,
    SERVICE_REOPEN_TASK,
)
from .coordinator import TapDataCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    try:
        implementation = await config_entry_oauth2_flow.async_get_config_entry_implementation(hass, entry)
    except ValueError:
        implementation = _build_fallback_oauth_implementation(hass, entry)
        if implementation is None:
            raise

        _LOGGER.warning("OAuth implementation metadata missing for Tap entry %s, using fallback", entry.entry_id)
        hass.config_entries.async_update_entry(
            entry,
            data={**entry.data, "auth_implementation": DOMAIN},
        )

    oauth_session = config_entry_oauth2_flow.OAuth2Session(hass, entry, implementation)
    await oauth_session.async_ensure_token_valid()

    api = TapApiClient(oauth_session, entry.data[CONF_API_BASE_URL])
    coordinator = TapDataCoordinator(hass, api)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        DATA_API: api,
        DATA_COORDINATOR: coordinator,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    _register_services(hass)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
        if not hass.data[DOMAIN]:
            hass.data.pop(DOMAIN)
            _unregister_services(hass)
    return unload_ok


def _build_fallback_oauth_implementation(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> LocalOAuth2Implementation | None:
    client_id = entry.data.get(CONF_CLIENT_ID)
    cognito_domain = entry.data.get(CONF_COGNITO_DOMAIN)
    if not client_id or not cognito_domain:
        return None

    cognito_domain = str(cognito_domain).rstrip("/")
    return LocalOAuth2Implementation(
        hass=hass,
        domain=DOMAIN,
        client_id=str(client_id),
        client_secret="",
        authorize_url=f"{cognito_domain}/oauth2/authorize",
        token_url=f"{cognito_domain}/oauth2/token",
    )


def _first_api(hass: HomeAssistant) -> TapApiClient | None:
    domain_data = hass.data.get(DOMAIN, {})
    for item in domain_data.values():
        api = item.get(DATA_API)
        if api:
            return api
    return None


def _first_coordinator(hass: HomeAssistant) -> TapDataCoordinator | None:
    domain_data = hass.data.get(DOMAIN, {})
    for item in domain_data.values():
        coordinator = item.get(DATA_COORDINATOR)
        if coordinator:
            return coordinator
    return None


def _register_services(hass: HomeAssistant) -> None:
    if hass.services.has_service(DOMAIN, SERVICE_COMPLETE_TASK):
        return

    async def _handle_complete_task(call: ServiceCall) -> None:
        api = _first_api(hass)
        coordinator = _first_coordinator(hass)
        if not api or not coordinator:
            return
        await api.async_complete_task(call.data[ATTR_TASK_ID])
        await coordinator.async_request_refresh()

    async def _handle_reopen_task(call: ServiceCall) -> None:
        api = _first_api(hass)
        coordinator = _first_coordinator(hass)
        if not api or not coordinator:
            return
        await api.async_reopen_task(call.data[ATTR_TASK_ID])
        await coordinator.async_request_refresh()

    async def _handle_add_log_entry(call: ServiceCall) -> None:
        api = _first_api(hass)
        coordinator = _first_coordinator(hass)
        if not api or not coordinator:
            return
        await api.async_add_log_entry(call.data[ATTR_LOG_ID], call.data.get(ATTR_NOTE, ""))
        await coordinator.async_request_refresh()

    hass.services.async_register(
        DOMAIN,
        SERVICE_COMPLETE_TASK,
        _handle_complete_task,
        schema=vol.Schema({vol.Required(ATTR_TASK_ID): str}),
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_REOPEN_TASK,
        _handle_reopen_task,
        schema=vol.Schema({vol.Required(ATTR_TASK_ID): str}),
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_ADD_LOG_ENTRY,
        _handle_add_log_entry,
        schema=vol.Schema(
            {
                vol.Required(ATTR_LOG_ID): str,
                vol.Optional(ATTR_NOTE, default=""): str,
            }
        ),
    )


def _unregister_services(hass: HomeAssistant) -> None:
    if hass.services.has_service(DOMAIN, SERVICE_COMPLETE_TASK):
        hass.services.async_remove(DOMAIN, SERVICE_COMPLETE_TASK)
    if hass.services.has_service(DOMAIN, SERVICE_REOPEN_TASK):
        hass.services.async_remove(DOMAIN, SERVICE_REOPEN_TASK)
    if hass.services.has_service(DOMAIN, SERVICE_ADD_LOG_ENTRY):
        hass.services.async_remove(DOMAIN, SERVICE_ADD_LOG_ENTRY)
