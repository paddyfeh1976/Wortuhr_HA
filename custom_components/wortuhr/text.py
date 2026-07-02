"""Text input entity for Wortuhr."""

from __future__ import annotations

from homeassistant.components.text import TextEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .text_background_color_picker import WortuhrBackgroundColorPicker

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Wortuhr text entity."""
    host = config_entry.data.get(CONF_HOST)

    device_info = DeviceInfo(
        identifiers={(DOMAIN, host)},
        name="Wortuhr",
        manufacturer="Wortuhr",
        model="HTTP API",
        configuration_url=f"http://{host}",
    )

    async_add_entities(
        [
            WortuhrMessageText(hass, config_entry, device_info, host),
            WortuhrBackgroundColorPicker(hass, config_entry, device_info, host),
        ]
    )


class WortuhrMessageText(TextEntity):
    """Text entity to hold a message for show_text."""

    _attr_has_entity_name = True
    _attr_name = "3. Event/Nachricht Text"
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        device_info: DeviceInfo,
        host: str,
    ) -> None:
        self.hass = hass
        self.config_entry = config_entry
        self._attr_device_info = device_info
        self._host = host
        self._attr_unique_id = f"wortuhr_message_text_{config_entry.entry_id}"
        self._native_value: str = ""

    @property
    def native_value(self) -> str | None:
        return self._native_value

    async def async_set_value(self, value: str) -> None:
        self._native_value = value
        self.async_write_ha_state()
