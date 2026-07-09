import importlib
import sys
import types
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch


class _DummyEntry:
    entry_id = "entry-1"
    data = {"host": "1.2.3.4"}


def _install_homeassistant_stubs() -> None:
    homeassistant = types.ModuleType("homeassistant")
    const = types.ModuleType("homeassistant.const")
    const.CONF_HOST = "host"
    const.CONF_SCAN_INTERVAL = "scan_interval"

    class _Platform:
        BUTTON = "button"
        SELECT = "select"
        TEXT = "text"
        SWITCH = "switch"
        LIGHT = "light"
        SENSOR = "sensor"
        NOTIFY = "notify"

    const.Platform = _Platform

    core = types.ModuleType("homeassistant.core")

    class HomeAssistant:  # pragma: no cover - simple stub
        pass

    class ServiceCall:  # pragma: no cover - simple stub
        def __init__(self, data=None):
            self.data = data or {}

    core.HomeAssistant = HomeAssistant
    core.ServiceCall = ServiceCall

    config_entries = types.ModuleType("homeassistant.config_entries")

    class ConfigEntry:  # pragma: no cover - simple stub
        def __init__(self):
            self.entry_id = "entry-1"
            self.data = {}

    config_entries.ConfigEntry = ConfigEntry

    helpers = types.ModuleType("homeassistant.helpers")
    aiohttp_client = types.ModuleType("homeassistant.helpers.aiohttp_client")
    aiohttp_client.async_get_clientsession = lambda hass: object()

    update_coordinator = types.ModuleType("homeassistant.helpers.update_coordinator")

    class DataUpdateCoordinator:  # pragma: no cover - simple stub
        def __init__(self, *args, **kwargs):
            pass

        async def async_config_entry_first_refresh(self):
            return None

    class UpdateFailed(Exception):
        pass

    update_coordinator.DataUpdateCoordinator = DataUpdateCoordinator
    update_coordinator.UpdateFailed = UpdateFailed

    notify = types.ModuleType("homeassistant.components.notify")

    class NotifyEntity:  # pragma: no cover - simple stub
        pass

    notify.NotifyEntity = NotifyEntity

    sys.modules.setdefault("homeassistant", homeassistant)
    sys.modules.setdefault("homeassistant.const", const)
    sys.modules.setdefault("homeassistant.core", core)
    sys.modules.setdefault("homeassistant.config_entries", config_entries)
    sys.modules.setdefault("homeassistant.helpers", helpers)
    sys.modules.setdefault("homeassistant.helpers.aiohttp_client", aiohttp_client)
    sys.modules.setdefault("homeassistant.helpers.update_coordinator", update_coordinator)
    sys.modules.setdefault("homeassistant.components", types.ModuleType("homeassistant.components"))
    sys.modules.setdefault("homeassistant.components.notify", notify)


_install_homeassistant_stubs()


class _DummyServices:
    def __init__(self) -> None:
        self.registered = []

    def async_register(self, domain, service, func, schema=None):
        self.registered.append((domain, service, func, schema))

    def has_service(self, domain, service):
        return any(item[0] == domain and item[1] == service for item in self.registered)


class NotifyEntityTests(unittest.IsolatedAsyncioTestCase):
    async def test_notify_entity_uses_main_wortuhr_device(self) -> None:
        import custom_components.wortuhr.notify as notify_module

        module = importlib.reload(notify_module)
        entry = SimpleNamespace(entry_id="entry-1", data={"host": "192.168.1.10"})

        entity = module.WortuhrNotificationEntity(hass=object(), entry=entry)

        self.assertEqual(entity.entity_id, "notify.wortuhr")
        self.assertEqual(entity.device_info["identifiers"], {(module.DOMAIN, "192.168.1.10")})

    async def test_send_message_uses_show_text(self) -> None:
        import custom_components.wortuhr.notify as notify_module

        module = importlib.reload(notify_module)
        entity = module.WortuhrNotificationEntity(hass=object(), entry=_DummyEntry())
        entity._host = "1.2.3.4"

        self.assertEqual(entity.entity_id, "notify.wortuhr")

        with patch.object(module, "async_show_text", new=AsyncMock(return_value="ok")) as mocked:
            await entity.async_send_message("hello world", title="Title", data={"color": 5, "buzzer": 1})

        mocked.assert_awaited_once_with(
            entity.hass,
            "1.2.3.4",
            "Title: hello world",
            5,
            1,
        )

    async def test_setup_entry_registers_notify_service(self) -> None:
        import custom_components.wortuhr.services as services_module

        module = importlib.reload(services_module)
        hass = SimpleNamespace(services=_DummyServices(), data={})

        await module.async_setup_services(hass)

        self.assertTrue(hass.services.has_service("notify", "wortuhr"))


if __name__ == "__main__":
    unittest.main()
