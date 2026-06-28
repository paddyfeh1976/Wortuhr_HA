"""Button to reboot the Wortuhr."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .services import async_reboot
from .button import WortuhrButton


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