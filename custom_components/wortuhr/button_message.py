"""Button to show the current message on the Wortuhr."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import COLOR_OPTIONS, DOMAIN
from .services import async_show_text


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    host = config_entry.data.get(CONF_HOST)

    device_info = DeviceInfo(
        identifiers={(DOMAIN, host)},
        name="Wortuhr",
        manufacturer="Wortuhr",
        model="HTTP API",
        configuration_url=f"http://{host}",
    )

    async_add_entities([WortuhrShowMessageButton(hass, config_entry, device_info, host)])


class WortuhrShowMessageButton(ButtonEntity):
    _attr_has_entity_name = True
    _attr_name = "Nachricht anzeigen"
    _attr_icon = "mdi:message-text"

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry, device_info: DeviceInfo, host: str) -> None:
        self.hass = hass
        self.config_entry = config_entry
        self._attr_device_info = device_info
        self._host = host
        self._attr_unique_id = f"wortuhr_show_message_{config_entry.entry_id}"

    async def async_press(self) -> None:
        # Resolve entity_ids from the entity registry using unique_id
        registry = er.async_get(self.hass)
        text_entity_id = registry.async_get_entity_id(
            "text",
            DOMAIN,
            f"wortuhr_message_text_{self.config_entry.entry_id}",
        )
        color_entity_id = registry.async_get_entity_id(
            "select",
            DOMAIN,
            f"wortuhr_message_color_select_{self.config_entry.entry_id}",
        )

        message_state = self.hass.states.get(text_entity_id) if text_entity_id else None
        color_state = self.hass.states.get(color_entity_id) if color_entity_id else None

        text = message_state.state if message_state else ""
        color = COLOR_OPTIONS.get(color_state.state, 0) if color_state else 0

        await async_show_text(self.hass, self._host, text, color, 0)
