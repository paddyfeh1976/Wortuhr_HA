"""Select entity for Wortuhr event pre-animation."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, EVENT_ANIMATION_OPTIONS


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

    async_add_entities([WortuhrPreAnimationSelect(hass, config_entry, device_info, host)])


class WortuhrPreAnimationSelect(SelectEntity):
    _attr_has_entity_name = True
    _attr_name = "1. Event Voranimation"
    _attr_entity_category = EntityCategory.CONFIG
    _attr_options = list(EVENT_ANIMATION_OPTIONS.keys())
    _attr_icon = "mdi:animation-play"

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
        self._attr_unique_id = f"wortuhr_pre_animation_select_{config_entry.entry_id}"
        self._current = " "

    @property
    def current_option(self) -> str | None:
        return self._current

    async def async_select_option(self, option: str) -> None:
        if option not in EVENT_ANIMATION_OPTIONS:
            return
        self._current = option
        self.async_write_ha_state()
