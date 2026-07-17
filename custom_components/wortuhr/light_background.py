"""Light entity for Wortuhr background color control."""
from __future__ import annotations

from typing import Any
import logging

from homeassistant.components.light import (
    LightEntity, 
    ColorMode, 
    ATTR_RGB_COLOR
)
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, STATE_ON
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util.color import color_rgb_to_hex

from .const import DOMAIN
from .services import async_set_setting
from .helpers import async_get_entity_id_by_unique_id

_LOGGER = logging.getLogger(__name__)

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
    async_add_entities([WortuhrBackgroundLight(hass, config_entry, device_info, host)])


class WortuhrBackgroundLight(LightEntity, RestoreEntity):
    _attr_has_entity_name = True
    _attr_name = "Hintergrund Farbe"
    _attr_icon = "mdi:palette"
    
    _attr_color_mode = ColorMode.RGB
    _attr_supported_color_modes = {ColorMode.RGB}

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
        self._entry_id = config_entry.entry_id
        self._attr_unique_id = f"wortuhr_background_light_{self._entry_id}"
        self._is_on = True
        self._rgb_color = (26, 0, 188)  # Entspricht dem alten Standard #1A00BC
        
        # Ziel-Verknüpfung zum Background-Option Select
        self._target_select_unique_id = f"wortuhr_background_option_{self._entry_id}"

    async def async_added_to_hass(self) -> None:
        """Wird aufgerufen, wenn die Entität zu Home Assistant hinzugefügt wurde."""
        await super().async_added_to_hass()
        
        last_state = await self.async_get_last_state()
        if last_state is not None:
            self._is_on = last_state.state == STATE_ON   

            if ATTR_RGB_COLOR in last_state.attributes:
                self._rgb_color = tuple(last_state.attributes[ATTR_RGB_COLOR])

    @property
    def is_on(self) -> bool:
        return self._is_on

    @property
    def rgb_color(self) -> tuple[int, int, int] | None:
        return self._rgb_color

    async def async_turn_on(self, **kwargs: Any) -> None:
        self._is_on = True
        
        # 1. Farbwahl verarbeiten und in Hex umrechnen
        if ATTR_RGB_COLOR in kwargs:
            self._rgb_color = kwargs[ATTR_RGB_COLOR]
        
        # Erzeuge den Hex-String (z.B. "#1a00bc") für die API
        hex_color = color_rgb_to_hex(self._rgb_color[0], self._rgb_color[1], self._rgb_color[2])
        await async_set_setting(self.hass, self._host, "Bgc", hex_color.upper())

        # 2. Synchronisation: Wenn das Select auf "Aus" steht, schalte es auf "Immer"
        select_entity_id = async_get_entity_id_by_unique_id(
            self.hass, "select", self._target_select_unique_id
        )
        if select_entity_id:
            select_state = self.hass.states.get(select_entity_id)
            if select_state and select_state.state == "Aus":
                await self.hass.services.async_call(
                    "select",
                    "select_option",
                    {"entity_id": select_entity_id, "option": "Immer"},
                    blocking=False,
                )

        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        self._is_on = False

        # Synchronisation: Wenn das Licht aus geht, stelle das Select auf "Aus"
        # Hinweis: Das Select wird dann seinerseits "bgce=0" an die Uhr senden.
        select_entity_id = async_get_entity_id_by_unique_id(
            self.hass, "select", self._target_select_unique_id
        )
        if select_entity_id:
            select_state = self.hass.states.get(select_entity_id)
            if select_state and select_state.state != "Aus":
                await self.hass.services.async_call(
                    "select",
                    "select_option",
                    {"entity_id": select_entity_id, "option": "Aus"},
                    blocking=False,
                )

        self.async_write_ha_state()