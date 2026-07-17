"""Select entity for Wortuhr message color."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, EntityCategory, STATE_ON, STATE_OFF
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, BACKGROUND_OPTIONS
from .services import async_set_setting
from .helpers import async_get_entity_id_by_unique_id


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

    async_add_entities([WortuhrBackgroundOptionSelect(hass, config_entry, device_info, host)])


class WortuhrBackgroundOptionSelect(SelectEntity, RestoreEntity):
    _attr_has_entity_name = True
    _attr_name = "Hintergrund"
    _attr_options = list(BACKGROUND_OPTIONS.keys())
    _attr_icon = "mdi:led-strip"
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
        self._entry_id = config_entry.entry_id
        self._host = host
        self._attr_unique_id = f"wortuhr_background_option_{self._entry_id}"

        # Ziel-Verknüpfung zum neuen Hintergrund-Licht        
        self._target_light_unique_id = f"wortuhr_background_light_{self._entry_id}"

    async def async_added_to_hass(self) -> None:
        """Wird aufgerufen, wenn die Entität zu Home Assistant hinzugefügt wurde."""
        # Wichtig: Immer die Basisklassen-Methode aufrufen
        await super().async_added_to_hass()
        
        # 1. Letzten Status wiederherstellen (falls verfügbar)
        last_state = await self.async_get_last_state()
        if last_state and last_state.state in self._attr_options:
            self._current_option = last_state.state
        else:
            # Fallback, falls kein gültiger Status gefunden wurde
            self._current_option = self._attr_options[0]

        # 2. Hier könntest du auch z. B. Dispatcher-Signale oder Webhook-Event          

    @property
    def current_option(self) -> str | None:
        return self._current_option

    async def async_select_option(self, option: str) -> None:
        if option not in BACKGROUND_OPTIONS:
            return

        await async_set_setting(
            self.hass,
            self._host,
            "bgce",
            BACKGROUND_OPTIONS[option],
        )
        self._current_option = option
        self.async_write_ha_state()

        # Dynamische Ermittlung der echten Licht-Entitäts-ID
        light_entity_id = async_get_entity_id_by_unique_id(
            self.hass, "light", self._target_light_unique_id
        )
        if not light_entity_id:
            return

        # UI-Synchronisation mit der Licht-Entität
        if option == "Aus":
            light_state = self.hass.states.get(light_entity_id)
            if light_state and light_state.state == STATE_ON:
                await self.hass.services.async_call(
                    "light",
                    "turn_off",
                    {"entity_id": light_entity_id},
                    blocking=False,
                )
        else:
            # Bei "Zeit" oder "Immer" soll das Licht im UI angehen
            light_state = self.hass.states.get(light_entity_id)
            if light_state and light_state.state == STATE_OFF:
                await self.hass.services.async_call(
                    "light",
                    "turn_on",
                    {"entity_id": light_entity_id},
                    blocking=False,
                )