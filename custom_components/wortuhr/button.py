"""Button platform for Wortuhr."""

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up button entities for Wortuhr."""
    host = config_entry.data.get(CONF_HOST)

    device_info = DeviceInfo(
        identifiers={(DOMAIN, host)},
        name="Wortuhr",
        manufacturer="Wortuhr",
        model="HTTP API",
        configuration_url=f"http://{host}",
    )

    buttons = [
        WortuhrRebootButton(hass, config_entry, device_info, host),
        WortuhrWiFiResetButton(hass, config_entry, device_info, host),
        WortuhrMp3ResetButton(hass, config_entry, device_info, host),
    ]

    async_add_entities(buttons)


class WortuhrButton(ButtonEntity):
    """Base class for Wortuhr button entities."""

    _attr_has_entity_name = True

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        device_info: DeviceInfo,
        host: str,
    ) -> None:
        """Initialize the button entity."""
        self.hass = hass
        self.config_entry = config_entry
        self._device_info = device_info
        self._host = host
        self._attr_device_info = device_info


class WortuhrRebootButton(WortuhrButton):
    """Button entity for rebooting Wortuhr."""

    _attr_name = "Reboot"
    _attr_unique_id = "wortuhr_reboot"
    _attr_icon = "mdi:restart"

    async def async_press(self) -> None:
        """Handle button press."""
        await self.hass.services.async_call(
            DOMAIN,
            "reboot",
            {"host": self._host},
        )


class WortuhrWiFiResetButton(WortuhrButton):
    """Button entity for WiFi reset."""

    _attr_name = "WiFi Reset"
    _attr_unique_id = "wortuhr_wifi_reset"
    _attr_icon = "mdi:wifi-remove"

    async def async_press(self) -> None:
        """Handle button press."""
        await self.hass.services.async_call(
            DOMAIN,
            "wifi_reset",
            {"host": self._host},
        )


class WortuhrMp3ResetButton(WortuhrButton):
    """Button entity for MP3 reset."""

    _attr_name = "MP3 Reset"
    _attr_unique_id = "wortuhr_mp3_reset"
    _attr_icon = "mdi:music-circle"

    async def async_press(self) -> None:
        """Handle button press."""
        await self.hass.services.async_call(
            DOMAIN,
            "mp3_reset",
            {"host": self._host},
        )
