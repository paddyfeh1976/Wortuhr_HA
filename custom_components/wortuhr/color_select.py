"""Select entity for Wortuhr message color."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, COLOR_OPTIONS


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

    async_add_entities([WortuhrColorSelect(hass, config_entry, device_info, host)])


class WortuhrColorSelect(SelectEntity):
    _attr_has_entity_name = True
    _attr_name = "Nachricht Farbe"
    _attr_options = list(COLOR_OPTIONS.keys())

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
        self._attr_unique_id = f"wortuhr_message_color_select_{config_entry.entry_id}"
        self._current = "Weiß"

    @property
    def current_option(self) -> str | None:
        return self._current

    async def async_select_option(self, option: str) -> None:
        if option not in COLOR_OPTIONS:
            return
        self._current = option
        self.async_write_ha_state()
