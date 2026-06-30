"""Select platform for Wortuhr."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .services import async_set_mode
from .select_mode import WortuhrModeSelect
from .select_message_text_color import WortuhrMessageTextColorSelect
from .select_event_post_ani import WortuhrPostAnimationSelect
from .select_event_pre_ani  import WortuhrPreAnimationSelect
from .select_led_color import WortuhrLedColorSelect
from .select_minute_led_color import WortuhrMinuteLedColorSelect
from .select_background_option import WortuhrBackgroundOptionSelect


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Wortuhr select entity."""
    host = config_entry.data.get(CONF_HOST)

    device_info = DeviceInfo(
        identifiers={(DOMAIN, host)},
        name="Wortuhr",
        manufacturer="Wortuhr",
        model="HTTP API",
        configuration_url=f"http://{host}",
    )

    async_add_entities(
        [
            WortuhrModeSelect(hass, config_entry, device_info, host),
            WortuhrMessageTextColorSelect(hass, config_entry, device_info, host),
            WortuhrPreAnimationSelect(hass, config_entry, device_info, host),
            WortuhrPostAnimationSelect(hass, config_entry, device_info, host),
            WortuhrLedColorSelect(hass, config_entry, device_info, host),
            WortuhrMinuteLedColorSelect(hass, config_entry, device_info, host),
            WortuhrBackgroundOptionSelect(hass, config_entry, device_info, host),   
        ]
    )
