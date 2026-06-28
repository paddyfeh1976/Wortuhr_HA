"""Button to show the current message on the Wortuhr."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .services import async_reboot
from .button import WortuhrButton


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    host = config_entry.data.get(CONF_HOST)

    device_info = DeviceInfo(
        identifiers={(DOMAIN, host)},
        name="Wortuhr",
        manufacturer="Wortuhr",
        model="HTTP API",
        configuration_url=f"http://{host}",
    )

    async_add_entities([WortuhrRebootButton(hass, config_entry, device_info, host)])


class WortuhrRebootButton(WortuhrButton):
    """Button entity for rebooting Wortuhr."""

    _attr_name = "Reboot"
    _attr_icon = "mdi:restart"
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        device_info: DeviceInfo,
        host: str,
    ) -> None:
        super().__init__(hass, config_entry, device_info, host)
        self._attr_unique_id = f"wortuhr_reboot_{config_entry.entry_id}"

    async def async_press(self) -> None:
        """Handle button press."""
        await async_reboot(self.hass, self._host)