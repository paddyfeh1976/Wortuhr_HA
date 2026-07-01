"""Light entity for Wortuhr brightness control."""
from __future__ import annotations

from typing import Any
from homeassistant.components.light import LightEntity, ColorMode, ATTR_BRIGHTNESS
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, STATE_ON
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .services import async_set_mode, async_set_setting

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
    async_add_entities([WortuhrMainWithBrightnessLight(hass, config_entry, device_info, host)])

class WortuhrMainWithBrightnessLight(LightEntity, RestoreEntity):
    _attr_has_entity_name = True
    _attr_name = "Wortuhr mit Helligkeit"
    _attr_color_mode = ColorMode.BRIGHTNESS
    _attr_supported_color_modes = {ColorMode.BRIGHTNESS}
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
        self._attr_unique_id = f"wortuhr_light_with_brightness_{config_entry.entry_id}"
        self._brightness = 127 # Startwert (entspricht ca 50%)
        self._is_on = True

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

        # 2. Hier könntest du auch z. B. Dispatcher-Signale oder Webhook-Event           

    @property
    def is_on(self) -> bool:
        return self._is_on

    @property
    def brightness(self) -> int:
        return self._brightness

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Wortuhr einschalten / Helligkeit ändern."""
        self._is_on = True

        # Falls der Schieberegler bewegt wurde, den neuen HA-Wert (0-255) abfangen
        if ATTR_BRIGHTNESS in kwargs:
            self._brightness = kwargs[ATTR_BRIGHTNESS]

        await async_set_mode(self.hass, self._host, 0)

        # Umrechnung des HA-Wertes (0-255) in Prozent (0-100) für die commitSettings-API
        pct_val = int((self._brightness / 255.0) * 100)
        if pct_val == 0:
            pct_val = 1 # Schutz vor 0%, wenn eingeschaltet wird
            
        # Sendet die Helligkeit an das Gerät
        await async_set_setting(self.hass, self._host, "br", pct_val)

        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await async_set_mode(self.hass, self._host, 17)
        self._is_on = False
        self.async_write_ha_state()