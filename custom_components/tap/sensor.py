from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DATA_COORDINATOR, DOMAIN
from .coordinator import TapDataCoordinator


@dataclass(frozen=True)
class TapSummaryDescription(SensorEntityDescription):
    data_key: str = ""


SUMMARY_SENSORS: tuple[TapSummaryDescription, ...] = (
    TapSummaryDescription(
        key="tasks_total",
        name="Tap Tasks Total",
        icon="mdi:check-all",
        data_key="tasksTotal",
    ),
    TapSummaryDescription(
        key="tasks_overdue",
        name="Tap Tasks Overdue",
        icon="mdi:alert-circle",
        data_key="tasksOverdue",
    ),
    TapSummaryDescription(
        key="tasks_due_soon",
        name="Tap Tasks Due Soon",
        icon="mdi:clock-alert",
        data_key="tasksDueSoon",
    ),
    TapSummaryDescription(
        key="tasks_completed_this_interval",
        name="Tap Tasks Completed This Interval",
        icon="mdi:check-circle",
        data_key="tasksCompletedThisInterval",
    ),
    TapSummaryDescription(
        key="events_active",
        name="Tap Events Active",
        icon="mdi:calendar-clock",
        data_key="eventsActive",
    ),
    TapSummaryDescription(
        key="events_completed",
        name="Tap Events Completed",
        icon="mdi:calendar-check",
        data_key="eventsCompleted",
    ),
    TapSummaryDescription(
        key="logs_total",
        name="Tap Logs Total",
        icon="mdi:notebook",
        data_key="logsTotal",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: TapDataCoordinator = hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR]
    entry_data = hass.data[DOMAIN][entry.entry_id]
    known_dynamic_ids: set[str] = entry_data.setdefault("known_dynamic_ids", set())

    initial_entities: list[SensorEntity] = [TapSummarySensor(coordinator, entry, description) for description in SUMMARY_SENSORS]
    dynamic_entities = _build_dynamic_entities(coordinator, entry, known_dynamic_ids)
    initial_entities.extend(dynamic_entities)
    async_add_entities(initial_entities)

    @callback
    def _handle_coordinator_update() -> None:
        new_entities = _build_dynamic_entities(coordinator, entry, known_dynamic_ids)
        if new_entities:
            async_add_entities(new_entities)

    unsub = coordinator.async_add_listener(_handle_coordinator_update)
    listeners = entry_data.setdefault("entity_listeners", [])
    listeners.append(unsub)
    entry.async_on_unload(unsub)


def _build_dynamic_entities(
    coordinator: TapDataCoordinator,
    entry: ConfigEntry,
    known_dynamic_ids: set[str],
) -> list[SensorEntity]:
    data = coordinator.data or {}
    entities: list[SensorEntity] = []

    for task in data.get("tasks", []):
        task_id = str(task.get("id", ""))
        if not task_id:
            continue
        key = f"task:{task_id}"
        if key in known_dynamic_ids:
            continue
        known_dynamic_ids.add(key)
        entities.append(TapTaskSensor(coordinator, entry, task_id))

    for event in data.get("events", []):
        event_id = str(event.get("id", ""))
        if not event_id:
            continue
        key = f"event:{event_id}"
        if key in known_dynamic_ids:
            continue
        known_dynamic_ids.add(key)
        entities.append(TapEventSensor(coordinator, entry, event_id))

    for log in data.get("logs", []):
        log_id = str(log.get("id", ""))
        if not log_id:
            continue
        key = f"log:{log_id}"
        if key in known_dynamic_ids:
            continue
        known_dynamic_ids.add(key)
        entities.append(TapLogSensor(coordinator, entry, log_id))

    return entities


class TapSummarySensor(CoordinatorEntity[TapDataCoordinator], SensorEntity):
    entity_description: TapSummaryDescription

    def __init__(
        self,
        coordinator: TapDataCoordinator,
        entry: ConfigEntry,
        description: TapSummaryDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_has_entity_name = True

    @property
    def native_value(self) -> Any:
        summary = (self.coordinator.data or {}).get("summary", {})
        return summary.get(self.entity_description.data_key)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        summary = (self.coordinator.data or {}).get("summary", {})
        generated_at = summary.get("generatedAt")
        return {"generated_at": generated_at} if generated_at else None


class _TapItemSensor(CoordinatorEntity[TapDataCoordinator], SensorEntity):
    _entry_id: str
    _item_id: str
    _item_type: str

    def __init__(self, coordinator: TapDataCoordinator, entry: ConfigEntry, item_id: str, item_type: str) -> None:
        super().__init__(coordinator)
        self._entry_id = entry.entry_id
        self._item_id = item_id
        self._item_type = item_type
        self._attr_unique_id = f"{entry.entry_id}_{item_type}_{item_id}"
        self._attr_has_entity_name = True

    def _collection(self) -> list[dict[str, Any]]:
        data = self.coordinator.data or {}
        if self._item_type == "task":
            return data.get("tasks", [])
        if self._item_type == "event":
            return data.get("events", [])
        return data.get("logs", [])

    def _item(self) -> dict[str, Any] | None:
        for candidate in self._collection():
            if str(candidate.get("id", "")) == self._item_id:
                return candidate
        return None

    @property
    def available(self) -> bool:
        return self._item() is not None and super().available


class TapTaskSensor(_TapItemSensor):
    def __init__(self, coordinator: TapDataCoordinator, entry: ConfigEntry, task_id: str) -> None:
        super().__init__(coordinator, entry, task_id, "task")
        self._attr_icon = "mdi:checkbox-marked-circle-outline"

    @property
    def name(self) -> str | None:
        task = self._item()
        if not task:
            return "Tap Task"
        return f"Tap Task {task.get('name', self._item_id)}"

    @property
    def native_value(self) -> Any:
        task = self._item()
        return task.get("status") if task else None

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        task = self._item()
        if not task:
            return None
        return {
            "task_id": task.get("id"),
            "is_complete_this_interval": task.get("isCompleteThisInterval"),
            "is_overdue": task.get("isOverdue"),
            "interval_days": task.get("intervalDays"),
            "times_per_day": task.get("timesPerDay"),
            "last_done": task.get("lastDone"),
            "next_due_at": task.get("nextDueAt"),
            "total_completions": task.get("totalCompletions"),
            "recent_completions": task.get("recentCompletions", []),
            "updated_at": task.get("updatedAt"),
        }


class TapEventSensor(_TapItemSensor):
    def __init__(self, coordinator: TapDataCoordinator, entry: ConfigEntry, event_id: str) -> None:
        super().__init__(coordinator, entry, event_id, "event")
        self._attr_icon = "mdi:calendar"

    @property
    def name(self) -> str | None:
        event = self._item()
        if not event:
            return "Tap Event"
        return f"Tap Event {event.get('title', self._item_id)}"

    @property
    def native_value(self) -> Any:
        event = self._item()
        if not event:
            return None
        return "completed" if event.get("isComplete") else "upcoming"

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        event = self._item()
        if not event:
            return None
        return {
            "event_id": event.get("id"),
            "title": event.get("title"),
            "emoji": event.get("emoji"),
            "notes": event.get("notes"),
            "start_date": event.get("startDate"),
            "target_date": event.get("targetDate"),
            "is_complete": event.get("isComplete"),
            "progress": event.get("progress"),
            "updated_at": event.get("updatedAt"),
        }


class TapLogSensor(_TapItemSensor):
    def __init__(self, coordinator: TapDataCoordinator, entry: ConfigEntry, log_id: str) -> None:
        super().__init__(coordinator, entry, log_id, "log")
        self._attr_icon = "mdi:notebook-outline"

    @property
    def name(self) -> str | None:
        log = self._item()
        if not log:
            return "Tap Log"
        return f"Tap Log {log.get('title', self._item_id)}"

    @property
    def native_value(self) -> Any:
        log = self._item()
        if not log:
            return None
        return log.get("entryCount", 0)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        log = self._item()
        if not log:
            return None
        return {
            "log_id": log.get("id"),
            "title": log.get("title"),
            "entry_count": log.get("entryCount", 0),
            "recent_entries": log.get("recentEntries", []),
            "updated_at": log.get("updatedAt"),
        }
