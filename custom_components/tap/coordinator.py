from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import TapApiClient
from .const import DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


class TapDataCoordinator(DataUpdateCoordinator[dict]):
    def __init__(
        self,
        hass: HomeAssistant,
        api: TapApiClient,
        update_interval: timedelta = DEFAULT_SCAN_INTERVAL,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="tap_data",
            update_interval=update_interval,
        )
        self.api = api

    async def _async_update_data(self) -> dict:
        try:
            summary = await self.api.async_get_summary()
            tasks = await self.api.async_get_tasks()
            events = await self.api.async_get_events()
            logs = await self.api.async_get_logs()
            return {
                "summary": summary,
                "tasks": tasks.get("tasks", []),
                "events": events.get("events", []),
                "logs": logs.get("logs", []),
            }
        except Exception as err:  # noqa: BLE001
            raise UpdateFailed(str(err)) from err
