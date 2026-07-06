from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, EntityCategory, PERCENTAGE, SIGNAL_STRENGTH_DECIBELS_MILLIWATT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator

from .const import DOMAIN

@dataclass(frozen=True, kw_only=True)
class WortuhrSensorEntityDescription(SensorEntityDescription):
    """Beschreibungsklasse mit Value-Extractor Funktion."""
    value_fn: Callable[[dict[str, Any]], Any]


# Liste aller Sensoren. Einige werden initial deaktiviert (enabled_default=False)
SENSOR_DESCRIPTIONS: tuple[WortuhrSensorEntityDescription, ...] = (
    # --- DIAGNOSE SENSOREN (STANDARD AKTIVIERT) ---
    WortuhrSensorEntityDescription(
        key="wifi_rssi",
        name="WLAN Signalstärke",
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("wifi", {}).get("rssi"),
    ),
    WortuhrSensorEntityDescription(
        key="system_freeheap",
        name="Freier Heap Speicher",
        native_unit_of_measurement="B",
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("system", {}).get("freeheap"),
    ),
    WortuhrSensorEntityDescription(
        key="system_version",
        name="Firmware Version",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("version"),
    ),
    
    # --- DIAGNOSE SENSOREN (INITIAL DEAKTIVIERT!) ---
    WortuhrSensorEntityDescription(
        key="wifi_bssid",
        name="WLAN BSSID",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False, # <--- HIER DEAKTIVIERT!
        value_fn=lambda data: data.get("wifi", {}).get("bssid"),
    ),
    WortuhrSensorEntityDescription(
        key="system_heapfragmentation",
        name="Heap Fragmentierung",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False, # <--- HIER DEAKTIVIERT!
        value_fn=lambda data: data.get("system", {}).get("heapfragmentation"),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Wortuhr sensors based on config entry."""
    entry_data = hass.data[DOMAIN][config_entry.entry_id]
    coordinator: DataUpdateCoordinator = entry_data["coordinator"]
    host = entry_data["data"][CONF_HOST]

    device_info = DeviceInfo(
        identifiers={(DOMAIN, host)},
        name="Wortuhr",
        manufacturer="Wortuhr",
        model="HTTP API",
        configuration_url=f"http://{host}",
    )

    # Erstelle alle Entitäten aus den Definitionen
    entities = [
        WortuhrSensorEntity(coordinator, description, device_info)
        for description in SENSOR_DESCRIPTIONS
    ]
    
    async_add_entities(entities)


class WortuhrSensorEntity(CoordinatorEntity, SensorEntity):
    """Repräsentation eines Wortuhr Sensors."""

    entity_description: WortuhrSensorEntityDescription

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        description: WortuhrSensorEntityDescription,
        device_info: DeviceInfo,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_device_info = device_info
        # Eindeutige ID generieren
        self._attr_unique_id = f"{coordinator.name}_{description.key}"

    @property
    def native_value(self) -> Any:
        """Gibt den Zustand des Sensors aus dem Koordinator-Cache zurück."""
        if not self.coordinator.data:
            return None
        return self.entity_description.value_fn(self.coordinator.data)