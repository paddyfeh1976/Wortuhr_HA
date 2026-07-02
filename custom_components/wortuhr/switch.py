"""Switch entity for Wortuhr auto brightness."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .switch_automatic_brigthness import WortuhrAutoBrightnessSwitch
from .switch_it_is import WortuhrItIsSwitch
from .switch_on_off import WortuhrOnOffSwitch

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
    async_add_entities(
        [
            WortuhrAutoBrightnessSwitch(hass, config_entry, device_info, host),
            WortuhrItIsSwitch(hass, config_entry, device_info, host),
        ]
    )

