from urllib.parse import urlencode

from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN

DEFAULT_HOST = "192.168.178.79"


def _build_url(host: str, path: str, params: dict | None = None) -> str:
    url = f"http://{host}/{path}"
    if params:
        params = {k: v for k, v in params.items() if v is not None and v != ""}
        query = urlencode(params)
        url = f"{url}?{query}"
    return url


async def request(hass: HomeAssistant, url: str) -> str:
    session = async_get_clientsession(hass)
    async with session.get(url, timeout=10) as response:
        response.raise_for_status()
        return await response.text()


def _get_host(hass: HomeAssistant, call: ServiceCall) -> str:
    """Abrufen der Host-IP aus Service-Call oder Konfiguration."""
    # Falls host im Service-Call angegeben, verwende diese
    if CONF_HOST in call.data:
        return call.data[CONF_HOST]
    
    # Sonst: Erste konfigurierte Host-IP verwenden
    entries = hass.data.get(DOMAIN, {})
    if entries:
        first_entry_data = next(iter(entries.values()))
        return first_entry_data.get(CONF_HOST, DEFAULT_HOST)
    
    return DEFAULT_HOST


async def async_setup_services(hass: HomeAssistant):

    async def show_text(call: ServiceCall):
        host = _get_host(hass, call)
        url = _build_url(
            host,
            "showText",
            {
                "buzzer": call.data.get("buzzer", 0),
                "color": call.data.get("color", 0),
                "text": call.data["text"],
            },
        )

        await request(hass, url)

    async def show_event(call: ServiceCall):
        host = _get_host(hass, call)
        url = _build_url(
            host,
            "setEvent",
            {
                "text": call.data["text"],
                "color": call.data.get("color", 0),
                "audio": call.data.get("audio", 0),
                "preani": call.data.get("preani", ""),
                "postani": call.data.get("postani", ""),
            },
        )

        await request(hass, url)

    async def play_audio(call: ServiceCall):
        host = _get_host(hass, call)
        url = _build_url(
            host,
            "PlayAudio",
            {
                "soundfile": call.data["soundfile"],
                "volume": call.data.get("volume", 0),
            },
        )

        await request(hass, url)

    async def set_mode(call: ServiceCall):
        host = _get_host(hass, call)
        url = _build_url(
            host,
            "control",
            {
                "mode": call.data["mode"],
                "sound": int(call.data.get("sound", False)),
            },
        )

        await request(hass, url)

    async def reboot(call: ServiceCall):
        host = _get_host(hass, call)
        await request(hass, f"http://{host}/reboot")

    async def wifi_reset(call: ServiceCall):
        host = _get_host(hass, call)
        await request(hass, f"http://{host}/wifireset")

    async def mp3_reset(call: ServiceCall):
        host = _get_host(hass, call)
        await request(hass, f"http://{host}/mp3reset")

    hass.services.async_register(
        DOMAIN,
        "show_text",
        show_text
    )

    hass.services.async_register(
        DOMAIN,
        "show_event",
        show_event
    )

    hass.services.async_register(
        DOMAIN,
        "play_audio",
        play_audio
    )

    hass.services.async_register(
        DOMAIN,
        "set_mode",
        set_mode
    )

    hass.services.async_register(
        DOMAIN,
        "reboot",
        reboot
    )

    hass.services.async_register(
        DOMAIN,
        "wifi_reset",
        wifi_reset
    )

    hass.services.async_register(
        DOMAIN,
        "mp3_reset",
        mp3_reset
    )