"""Select entity for Wortuhr message color."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, COLOR_OPTIONS
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

    async_add_entities([WortuhrLedColorSelect(hass, config_entry, device_info, host)])


class WortuhrLedColorSelect(SelectEntity):
    _attr_has_entity_name = True
    _attr_name = "Led Farbe"
    _attr_options = list(COLOR_OPTIONS.keys())
    _attr_icon = "mdi:led-strip-variant"
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
        self._attr_unique_id = f"wortuhr_led_color_select_{config_entry.entry_id}"
        self._current = "Weiß"

    async def async_added_to_hass(self) -> None:
        """Wird aufgerufen, wenn die Entität geladen wird."""
        await super().async_added_to_hass()
        if (old_state := await self.async_get_last_state()) is not None:
            # Prüfen, ob der alte Zustand einer der erlaubten Werte ist
            if old_state.state in self._attr_options:
                self._current = old_state.state

    @property
    def current_option(self) -> str | None:
        return self._current

    async def async_select_option(self, option: str) -> None:
        if option not in COLOR_OPTIONS:
            return

        await async_set_setting(
            self.hass,
            self._host,
            "co",
            COLOR_OPTIONS[option],
        )
        self._current = option
        self.async_write_ha_state()
