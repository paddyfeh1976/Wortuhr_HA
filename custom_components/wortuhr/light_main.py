"""Light entity for Wortuhr brightness control."""
from __future__ import annotations

import math
from typing import Any
from homeassistant.components.light import (
    LightEntity, 
    ColorMode, 
    ATTR_BRIGHTNESS, 
    ATTR_EFFECT,
    ATTR_RGB_COLOR,
    LightEntityFeature
)
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, STATE_ON, STATE_OFF
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util.color import brightness_to_value
from homeassistant.helpers import entity_registry as er

from .const import DOMAIN, MODE_OPTIONS
from .services import async_set_mode, async_set_setting
from .color_mapper import WortuhrColorMapper

import logging

# Logger für diese Datei initialisieren
_LOGGER = logging.getLogger(__name__)

BRIGHTNESS_SCALE = (1, 100)  # Wortuhr brightness scale from 1 to 100

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
    async_add_entities([WortuhrMainLight(hass, config_entry, device_info, host, config_entry.entry_id)])

class WortuhrMainLight(LightEntity, RestoreEntity):
    _attr_has_entity_name = True
    _attr_name = "Wortuhr"
    _attr_color_mode = ColorMode.RGB
    _attr_supported_color_modes = {ColorMode.RGB}
    _attr_icon = "mdi:dots-square"
    _attr_supported_features = LightEntityFeature.EFFECT

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
        self._attr_unique_id = f"wortuhr_main_{self._entry_id}"
        self._brightness = 127 # Startwert (entspricht ca 50%)
        self._is_on = True
        self._effect = "Zeit (Uhr)"

        self._rgb_color = (255, 255, 255)
        self._color_name = "Weiß"
        self._target_minutes_unique_id = f"wortuhr_minutes_{self._entry_id}"

    async def async_added_to_hass(self) -> None:
        """Wird aufgerufen, wenn die Entität zu Home Assistant hinzugefügt wurde."""
        # Wichtig: Immer die Basisklassen-Methode aufrufen
        await super().async_added_to_hass()
        
        # 1. Letzten Status wiederherstellen (falls verfügbar)
        last_state = await self.async_get_last_state()
        if last_state is not None:
            self._is_on = last_state.state == STATE_ON   

            # Hier wird die Helligkeit aus den Attributen des letzten Zustands geladen
            if ATTR_BRIGHTNESS in last_state.attributes:
                self._brightness = last_state.attributes[ATTR_BRIGHTNESS]    

            # Effekt/Modus-Text wiederherstellen
            if ATTR_EFFECT in last_state.attributes:
                self._effect = last_state.attributes[ATTR_EFFECT]                        

            if ATTR_RGB_COLOR in last_state.attributes:
                self._rgb_color = last_state.attributes[ATTR_RGB_COLOR]
        # 2. Hier könntest du auch z. B. Dispatcher-Signale oder Webhook-Event           

    @property
    def is_on(self) -> bool:
        return self._is_on

    @property
    def brightness(self) -> int | None:
        return self._brightness
    
    @property
    def rgb_color(self) -> tuple[int, int, int] | None:
        """Gibt die aktuell gesetzte RGB-Farbe an Home Assistant zurück."""
        return self._rgb_color

    @property
    def effect_list(self) -> list[str] | None:
        """Gibt die Liste der verfügbaren Effekte/Modi für das UI zurück."""
        # Nutzt die Keys deiner Konstante ("Zeit (Uhr)", "Ansage", "Wochentag", etc.)
        return list(MODE_OPTIONS.keys())

    @property
    def effect(self) -> str | None:
        """Gibt den aktuell aktiven Effekt/Modus zurück."""
        return self._effect    

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Wortuhr einschalten, Helligkeit ändern oder Effekt wechseln."""
        self._is_on = True

        # Szenario A: Es wurde ein Effekt aus dem Dropdown ausgewählt
        if ATTR_EFFECT in kwargs:
            new_effect = kwargs[ATTR_EFFECT]
            if new_effect in MODE_OPTIONS:
                self._effect = new_effect
                mode_id = MODE_OPTIONS[new_effect]
                _LOGGER.info("Wortuhr Effekt-Wechsel: %s (API Mode: %s)", new_effect, mode_id)
                # Setzt den ausgewählten API-Modus
                await async_set_mode(self.hass, self._host, mode_id)
        
        # Szenario B: Das Licht wurde einfach nur eingeschaltet (ohne Effekt-Wechsel)
        elif not kwargs:
            # Falls ein bestimmter Effekt gespeichert war, reaktivieren wir dessen Modus,
            # ansonsten fallen wir auf Modus 0 ("Zeit (Uhr)") zurück.
            mode_id = MODE_OPTIONS.get(self._effect, 0)
            await async_set_mode(self.hass, self._host, mode_id)

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
                "Wortuhr Farbe geändert: Wunsch-RGB=%s -> Gematcht auf: %s (API ID: %s)", 
                requested_rgb, color_name, color_id
            )
            
            # Sendet den Farb-Index an die Uhr via commitSettings
            await async_set_setting(self.hass, self._host, "co", color_id)

            # Wir holen uns die Entity Registry von Home Assistant
            entity_registry = er.async_get(self.hass)
            
            # Wir suchen die aktuelle Entity ID anhand der unveränderlichen Unique ID der Minuten
            minutes_entry = entity_registry.async_get_entity_id(
                "light", DOMAIN, self._target_minutes_unique_id
            )

            if minutes_entry:
                # Jetzt haben wir die echte aktuelle Entity ID (egal wie sie vom User benannt wurde!)
                minutes_state = self.hass.states.get(minutes_entry)

                # Wenn die Minutenpunkte-Lampe in HA ausgeschaltet ist, steuern wir sie mit
                if minutes_state is not None and minutes_state.state == STATE_OFF:
                    _LOGGER.info(
                        "Minuten Punkte (%s) sind ausgeschaltet. Hauptlicht übernimmt die Farbe (API ID: %s via 'cco')", 
                        minutes_entry, color_id
                    )
                    await async_set_setting(self.hass, self._host, "cco", color_id)

        # Helligkeit verarbeiten (falls Schieberegler bewegt wurde oder beim Einschalten)
        if ATTR_BRIGHTNESS in kwargs:
            self._brightness = kwargs[ATTR_BRIGHTNESS]

        # Umrechnung des HA-Wertes (0-255) in Prozent (0-100)
        pct_val = int(math.ceil(brightness_to_value(BRIGHTNESS_SCALE, self._brightness)))

        # Auf den nächsten Zehner runden
        pct_val = int(round(pct_val / 10.0) * 10)
        
        # Grenzwerte absichern
        if pct_val < 10:
            pct_val = 10
        elif pct_val > 100:
            pct_val = 100

        _LOGGER.info(
            "Wortuhr Helligkeitsänderung: HA-Wert=%s -> Berechneter API-Prozentwert=%s", 
            self._brightness, 
            pct_val
        )

        # Sendet die Helligkeit an das Gerät
        await async_set_setting(self.hass, self._host, "br", pct_val)

        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await async_set_mode(self.hass, self._host, 17)
        self._is_on = False
        self.async_write_ha_state()