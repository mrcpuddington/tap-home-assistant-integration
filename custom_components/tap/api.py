from __future__ import annotations

from collections.abc import Mapping
import uuid

from homeassistant.helpers.config_entry_oauth2_flow import OAuth2Session

from .const import (
    API_PATH_ADD_LOG_ENTRY,
    API_PATH_COMPLETE_TASK,
    API_PATH_EVENTS,
    API_PATH_LOGS,
    API_PATH_REOPEN_TASK,
    API_PATH_SUMMARY,
    API_PATH_TASKS,
)


class TapApiClient:
    def __init__(self, oauth_session: OAuth2Session, api_base_url: str) -> None:
        self._oauth_session = oauth_session
        self._api_base_url = api_base_url.rstrip("/")

    async def async_get_summary(self) -> dict:
        return await self._request("GET", API_PATH_SUMMARY)

    async def async_get_tasks(self) -> dict:
        return await self._request("GET", API_PATH_TASKS)

    async def async_get_events(self) -> dict:
        return await self._request("GET", API_PATH_EVENTS)

    async def async_get_logs(self) -> dict:
        return await self._request("GET", API_PATH_LOGS)

    async def async_complete_task(self, task_id: str) -> dict:
        return await self._request(
            "POST",
            API_PATH_COMPLETE_TASK,
            {
                "taskID": task_id,
                "idempotencyKey": str(uuid.uuid4()),
            },
        )

    async def async_reopen_task(self, task_id: str) -> dict:
        return await self._request(
            "POST",
            API_PATH_REOPEN_TASK,
            {
                "taskID": task_id,
                "idempotencyKey": str(uuid.uuid4()),
            },
        )

    async def async_add_log_entry(self, log_id: str, note: str) -> dict:
        return await self._request(
            "POST",
            API_PATH_ADD_LOG_ENTRY,
            {
                "logID": log_id,
                "note": note,
                "idempotencyKey": str(uuid.uuid4()),
            },
        )

    async def _request(self, method: str, path: str, body: Mapping | None = None) -> dict:
        url = f"{self._api_base_url}{path}"
        response = await self._oauth_session.async_request(method, url, json=body)
        response.raise_for_status()
        if not response.content:
            return {}
        return await response.json()
