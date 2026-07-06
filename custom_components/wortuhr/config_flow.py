import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN


class WortuhrConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Wortuhr."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            host = user_input.get(CONF_HOST)
            scan_interval = user_input.get(CONF_SCAN_INTERVAL, 60)

            # Prüfe Verbindung zum Gerät
            if not await self._check_connection(host):
                errors["base"] = "cannot_connect"
            else:
                # Prüfe ob bereits konfiguriert
                await self.async_set_unique_id(host)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"Wortuhr ({host})",
                    data={
                        CONF_HOST: host,
                        CONF_SCAN_INTERVAL: scan_interval,
                    },
                )

        data_schema = vol.Schema(
            {
                vol.Required(CONF_HOST, default="192.168.178.79"): str,
                vol.Required(CONF_SCAN_INTERVAL, default=60): vol.All(
                    vol.Coerce(int), vol.Range(min=5, max=3600)
                ),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={},
        )

    async def _check_connection(self, host: str) -> bool:
        """Prüfe die Verbindung zur Wortuhr."""
        try:
            session = async_get_clientsession(self.hass)
            async with session.get(f"http://{host}/apidata", timeout=5) as response:
                return response.status == 200
        except Exception:
            return False
