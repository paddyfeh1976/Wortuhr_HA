from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable
from datetime import datetime, timezone

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_HOST, 
    EntityCategory, 
    PERCENTAGE, 
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
    UnitOfTemperature,
    UnitOfPressure,
    UnitOfSpeed,
)
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
    # --- WIFI ---
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
        key="wifi_bssid",
        name="WLAN BSSID",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False, # <--- HIER DEAKTIVIERT!
        value_fn=lambda data: data.get("wifi", {}).get("bssid"),
    ),
# --- ZEITDATEN ---
    WortuhrSensorEntityDescription(
        key="time_starttime",
        name="Uhr Startzeit",
        device_class=SensorDeviceClass.TIMESTAMP,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False, # <--- HIER DEAKTIVIERT!
        # Konvertiert den Unix-Timestamp (Sekunden) in ein timezone-aware datetime Objekt
        value_fn=lambda data: datetime.fromtimestamp(
            data.get("time", {}).get("starttime"), timezone.utc
        ) if data.get("time", {}).get("starttime") else None,
    ),
    # --- SYSTEM / HARDWARE ---
    WortuhrSensorEntityDescription(
        key="system_board",
        name="Board Revision",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("system", {}).get("board"),
    ),
    WortuhrSensorEntityDescription(
        key="system_freeheap",
        name="Freier Heap Speicher",
        native_unit_of_measurement="B",
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False, # <--- HIER DEAKTIVIERT!
        value_fn=lambda data: data.get("system", {}).get("freeheap"),
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
    # --- LDR (LICHTSENSOR) ---
    WortuhrSensorEntityDescription(
        key="ldr_brightness",
        name="LED Helligkeit",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("ldr", {}).get("brightness"),
    ),
    WortuhrSensorEntityDescription(
        key="ldr_value",
        name="LDR Sensorwert RAW",
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False, # <--- HIER DEAKTIVIERT!
        value_fn=lambda data: data.get("ldr", {}).get("ldrvalue"),
    ),
    # --- BME280 INTERNER SENSOR ---
    WortuhrSensorEntityDescription(
        key="bme280_temperature",
        name="Innentemperatur",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False, # <--- HIER DEAKTIVIERT!
        value_fn=lambda data: data.get("bme280", {}).get("temperature"),
    ),
    WortuhrSensorEntityDescription(
        key="bme280_humidity",
        name="Innenluftfeuchtigkeit",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False, # <--- HIER DEAKTIVIERT!
        value_fn=lambda data: data.get("bme280", {}).get("humidity"),
    ),
    WortuhrSensorEntityDescription(
        key="bme280_pressure",
        name="Luftdruck (Absolut)",
        native_unit_of_measurement=UnitOfPressure.HPA,
        device_class=SensorDeviceClass.ATMOSPHERIC_PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False, # <--- HIER DEAKTIVIERT!
        value_fn=lambda data: data.get("bme280", {}).get("pressure"),
    ),
    WortuhrSensorEntityDescription(
        key="bme280_pressure_rel",
        name="Luftdruck (Relativ)",
        native_unit_of_measurement=UnitOfPressure.HPA,
        device_class=SensorDeviceClass.ATMOSPHERIC_PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False, # <--- HIER DEAKTIVIERT!
        value_fn=lambda data: data.get("bme280", {}).get("pressure_rel"),
    ),
    WortuhrSensorEntityDescription(
        key="bme280_pressure_diff",
        name="Luftdruck Tendenz",
        native_unit_of_measurement=UnitOfPressure.HPA,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False, # <--- HIER DEAKTIVIERT!
        value_fn=lambda data: data.get("bme280", {}).get("pressure_diff"),
    ),
    # --- OPENWEATHERMAP SENSOR ---
    WortuhrSensorEntityDescription(
        key="openweather_temperature",
        name="Außentemperatur (OWM)",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False, # <--- HIER DEAKTIVIERT!
        value_fn=lambda data: data.get("openweather", {}).get("temperature"),
    ),
    WortuhrSensorEntityDescription(
        key="openweather_humidity",
        name="Außenluftfeuchtigkeit (OWM)",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False, # <--- HIER DEAKTIVIERT!
        value_fn=lambda data: data.get("openweather", {}).get("humidity"),
    ),
    WortuhrSensorEntityDescription(
        key="openweather_pressure",
        name="Luftdruck (OWM)",
        native_unit_of_measurement=UnitOfPressure.HPA,
        device_class=SensorDeviceClass.ATMOSPHERIC_PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False, # <--- HIER DEAKTIVIERT!
        value_fn=lambda data: data.get("openweather", {}).get("pressure"),
    ),
    WortuhrSensorEntityDescription(
        key="openweather_windspeed",
        name="Windgeschwindigkeit (OWM)",
        native_unit_of_measurement=UnitOfSpeed.METERS_PER_SECOND,
        device_class=SensorDeviceClass.WIND_SPEED,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False, # <--- HIER DEAKTIVIERT!
        value_fn=lambda data: data.get("openweather", {}).get("windspeed"),
    ),
    # --- SONNE ---
    WortuhrSensorEntityDescription(
        key="sun_sunrise",
        name="Sonnenaufgang",
        device_class=SensorDeviceClass.TIMESTAMP,
        entity_registry_enabled_default=False, # <--- HIER DEAKTIVIERT!
        value_fn=lambda data: datetime.fromtimestamp(
            data.get("sun", {}).get("sunrise"), timezone.utc
        ) if data.get("sun", {}).get("sunrise") else None,
    ),
    WortuhrSensorEntityDescription(
        key="sun_sunset",
        name="Sonnenuntergang",
        device_class=SensorDeviceClass.TIMESTAMP,
        entity_registry_enabled_default=False, # <--- HIER DEAKTIVIERT!
        value_fn=lambda data: datetime.fromtimestamp(
            data.get("sun", {}).get("sunset"), timezone.utc
        ) if data.get("sun", {}).get("sunset") else None,
    ),

    WortuhrSensorEntityDescription(
        key="system_version",
        name="Firmware Version",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("version"),
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