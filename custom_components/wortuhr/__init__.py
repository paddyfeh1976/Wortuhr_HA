from datetime import timedelta
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform, CONF_HOST, CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN
from .services import async_setup_services

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [
    Platform.BUTTON,
    Platform.SELECT,
    Platform.TEXT,
    Platform.SWITCH,
    Platform.LIGHT,
    Platform.SENSOR,
    Platform.NOTIFY,
]


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Wortuhr integration services."""
    await async_setup_services(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Wortuhr from a config entry."""
    host = entry.data[CONF_HOST]
    scan_interval = entry.data.get(CONF_SCAN_INTERVAL, 60)
    session = async_get_clientsession(hass)

    # Zentraler DataUpdateCoordinator
    async def async_get_api_data():
        try:
            async with session.get(f"http://{host}/apidata", timeout=10) as response:
                if response.status != 200:
                    raise UpdateFailed(f"Fehler beim Abruf der API: {response.status}")
                return await response.json()
        except Exception as err:
            raise UpdateFailed(f"Kommunikationsfehler mit der Wortuhr: {err}")

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"Wortuhr {host} API",
        update_method=async_get_api_data,
        update_interval=timedelta(seconds=scan_interval),
    )

    # Ersten Abruf triggern; bei Startproblemen nicht die komplette Integration abbrechen
    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:
        _LOGGER.warning(
            "Erster API-Refresh fehlgeschlagen für %s: %s. Die Integration wird trotzdem geladen.",
            host,
            err,
        )
        coordinator.data = {}

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "data": entry.data
    }

    # Load button platform
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok and entry.entry_id in hass.data.get(DOMAIN, {}):
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok
