"""Light entity for Wortuhr brightness control."""
from __future__ import annotations

import math
from typing import Any
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

from .const import DOMAIN
from .services import async_set_mode, async_set_setting
from .color_mapper import WortuhrColorMapper

import logging

# Logger für diese Datei initialisieren
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
    async_add_entities([WortuhrMinutesLight(hass, config_entry, device_info, host)])

class WortuhrMinutesLight(LightEntity, RestoreEntity):
    _attr_has_entity_name = True
    _attr_name = "Minuten Leds"
    _attr_color_mode = ColorMode.RGB
    _attr_supported_color_modes = {ColorMode.RGB}
    _attr_icon = "mdi:dots-square"

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
        self._attr_unique_id = f"wortuhr_minutes_{config_entry.entry_id}"
        self._is_on = True
        self._rgb_color = (255, 255, 255)
        self._color_name = "Weiß"

    async def async_added_to_hass(self) -> None:
        """Wird aufgerufen, wenn die Entität zu Home Assistant hinzugefügt wurde."""
        # Wichtig: Immer die Basisklassen-Methode aufrufen
        await super().async_added_to_hass()
        
        # 1. Letzten Status wiederherstellen (falls verfügbar)
        last_state = await self.async_get_last_state()
        if last_state is not None:
            self._is_on = last_state.state == STATE_ON   
        if ATTR_RGB_COLOR in last_state.attributes:
                self._rgb_color = last_state.attributes[ATTR_RGB_COLOR]
        # 2. Hier könntest du auch z. B. Dispatcher-Signale oder Webhook-Event           

    @property
    def is_on(self) -> bool:
        return self._is_on
    
    @property
    def rgb_color(self) -> tuple[int, int, int] | None:
        """Gibt die aktuell gesetzte RGB-Farbe an Home Assistant zurück."""
        return self._rgb_color


    async def async_turn_on(self, **kwargs: Any) -> None:
        self._is_on = True
        await async_set_setting(self.hass, self._host, "ccc", 0)
        
        # FARBWAHL VERARBEITEN
        if ATTR_RGB_COLOR in kwargs:
            requested_rgb = kwargs[ATTR_RGB_COLOR]
            
            # Nutze den ausgelagerten Mapper für das euklidische Matching
            color_name, color_id, matched_rgb = WortuhrColorMapper.find_closest_color(requested_rgb)
            
            # Wir speichern das exakt gematchte RGB-Tupel, damit das HA-UI auf den 
            # Punkt "springt", den die Uhr real darstellen kann.
            self._rgb_color = matched_rgb
            self._color_name = color_name
            
            _LOGGER.info(
                "Wortuhr Minuten Farbe geändert: Wunsch-RGB=%s -> Gematcht auf: %s (API ID: %s)", 
                requested_rgb, color_name, color_id
            )
            
            # Sendet den Farb-Index an die Uhr via commitSettings
            await async_set_setting(self.hass, self._host, "cco", color_id)
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await async_set_setting(self.hass, self._host, "ccc", 4)
        self._is_on = False
        self.async_write_ha_state()