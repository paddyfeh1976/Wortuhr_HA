from urllib.parse import urlencode

from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN

import logging

# Logger für diese Datei initialisieren
_LOGGER = logging.getLogger(__name__)

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

        # --- HIER DIE LOG-AUSGABE EINFÜGEN ---
    _LOGGER.info(
        "Request abgesendet: URL=%s", 
        url
    )
    # -------------------------------------

    async with session.get(url, timeout=10) as response:
        response.raise_for_status()
        return await response.text()


async def async_show_text(
    hass: HomeAssistant,
    host: str,
    text: str,
    color: int,
    buzzer: int = 0,
) -> str:
    url = _build_url(
        host,
        "showText",
        {
            "buzzer": buzzer,
            "color": color,
            "text": text,
        },
    )
    return await request(hass, url)


async def async_show_event(
    hass: HomeAssistant,
    host: str,
    text: str,
    color: int,
    preani: str,
    postani: str,
    audio: int = 0,
) -> str:
    url = _build_url(
        host,
        "setEvent",
        {
            "text": text,
            "color": color,
            "audio": audio,
            "preani": preani,
            "postani": postani,
        },
    )
    return await request(hass, url)


async def async_play_audio(
    hass: HomeAssistant,
    host: str,
    soundfile: int,
    volume: int = 0,
) -> str:
    url = _build_url(
        host,
        "PlayAudio",
        {
            "soundfile": soundfile,
            "volume": volume,
        },
    )
    return await request(hass, url)


async def async_set_mode(
    hass: HomeAssistant,
    host: str,
    mode: int,
    sound: bool = False,
) -> str:
    url = _build_url(
        host,
        "control",
        {
            "mode": mode,
            "sound": int(sound),
        },
    )
    return await request(hass, url)

async def async_set_setting(
    hass: HomeAssistant,
    host: str,    
    key: str,
    value: any,
) -> str:
    url = _build_url(
        host,
        "commitSettings",
        {
            key: value,
        },
    )
    return await request(hass, url)


async def async_reboot(hass: HomeAssistant, host: str) -> str:
    return await request(hass, f"http://{host}/reboot")


async def async_wifi_reset(hass: HomeAssistant, host: str) -> str:
    return await request(hass, f"http://{host}/wifireset")


async def async_mp3_reset(hass: HomeAssistant, host: str) -> str:
    return await request(hass, f"http://{host}/mp3reset")


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
        await async_show_text(
            hass,
            host,
            call.data["text"],
            call.data.get("color", 0),
            call.data.get("buzzer", 0),
        )

    async def show_event(call: ServiceCall):
        host = _get_host(hass, call)

        text = call.data.get("text", "")
        color = call.data.get("color", 0)
        audio = call.data.get("audio", 0)
        preani = call.data.get("preani", "")
        postani = call.data.get("postani", "")

        if "rgb_color" in call.data and call.data["rgb_color"]:
            color = 0

        await async_show_event(
            hass,
            host,
            text,
            color,
            preani,
            postani,
            audio,
        )

    async def play_audio(call: ServiceCall):
        host = _get_host(hass, call)
        await async_play_audio(
            hass,
            host,
            call.data["soundfile"],
            call.data.get("volume", 0),
        )

    async def set_mode(call: ServiceCall):
        host = _get_host(hass, call)
        await async_set_mode(
            hass,
            host,
            call.data["mode"],
            bool(call.data.get("sound", False)),
        )

    async def reboot(call: ServiceCall):
        host = _get_host(hass, call)
        await async_reboot(hass, host)

    async def wifi_reset(call: ServiceCall):
        host = _get_host(hass, call)
        await async_wifi_reset(hass, host)

    async def mp3_reset(call: ServiceCall):
        host = _get_host(hass, call)
        await async_mp3_reset(hass, host)

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