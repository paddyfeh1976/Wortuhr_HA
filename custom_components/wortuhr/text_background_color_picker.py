"""Text entity used as Color Picker for Wortuhr background color."""
from __future__ import annotations

from homeassistant.components.text import TextEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .services import async_set_setting

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    host = config_entry.data.get(CONF_HOST)
    device_info = DeviceInfo(
        identifiers={(DOMAIN, host)},
        name="Wortuhr",
        manufacturer="Wortuhr",
        model="HTTP API",
        configuration_url=f"http://{host}",
    )
    async_add_entities([WortuhrBackgroundColorPicker(hass, config_entry, device_info, host)])

class WortuhrBackgroundColorPicker(TextEntity):
    _attr_has_entity_name = True
    _attr_name = "Hintergrund Farbe"
    _attr_icon = "mdi:palette"
    _attr_entity_category = EntityCategory.CONFIG
    
    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        device_info: DeviceInfo,
        host: str,
    ) -> None:
        self.hass = hass
        self._host = host
        self._attr_device_info = device_info
        self._attr_unique_id = f"wortuhr_bg_color_{config_entry.entry_id}"
        self._value = "#1A00BC"

    @property
    def native_value(self) -> str:
        return self._value

    async def async_set_value(self, value: str) -> None:
        # Falls der Picker den Wert ohne '#' liefert, fügen wir es an
        formatted_color = value if value.startswith("#") else f"#{value}"
        
        await async_set_setting(self.hass, self._host, "Bgc", formatted_color)
        self._value = formatted_color
        self.async_write_ha_state()