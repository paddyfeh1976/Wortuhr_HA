from urllib.parse import urlencode

from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv, device_registry as dr
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, EVENT_ANIMATION_OPTIONS
from .color_mapper import WortuhrColorMapper

import voluptuous as vol
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
    text: str = "",
    color_id: int = 1,
    audio_id: int | None = None,
    preani: str | None = None,
    postani: str | None = None,
) -> None:
    params = {
        "text": text,
        "color": color_id,
        "audio": audio_id,
        "preani": preani,
        "postani": postani,
    }
    url = _build_url(host, "showEvent", params)
    await request(hass, url)

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
    """Ermittelt die IP-Adresse (host) – entweder aus dem Target-Gerät, dem Textfeld oder als Fallback."""
    # 1. Option: Wurde eine IP-Adresse direkt als Text im Feld eingegeben?
    if "host" in call.data and call.data["host"]:
        return call.data["host"]

    # 2. Option: Wurde ein konkretes Gerät (Target) in der GUI ausgewählt?
    device_ids = call.data.get("device_id") or call.context.to_dict().get("device_id")
    if not device_ids and "device_id" in call.data:
        device_ids = call.data["device_id"]

    if device_ids:
        # Falls es eine Liste ist, nimm das erste gewählte Gerät
        device_id = device_ids[0] if isinstance(device_ids, list) else device_ids
        
        dev_reg = dr.async_get(hass)
        device = dev_reg.async_get(device_id)
        if device:
            for entry_id in device.config_entries:
                config_entry = hass.config_entries.async_get_entry(entry_id)
                if config_entry and CONF_HOST in config_entry.data:
                    return config_entry.data[CONF_HOST]

    # 3. Option (Fallback): Nimm einfach den ersten Eintrag der Wortuhr-Integration
    entries = hass.config_entries.async_entries(DOMAIN)
    if entries and CONF_HOST in entries[0].data:
        return entries[0].data[CONF_HOST]

    # Letzter Notanker
    return DEFAULT_HOST


async def async_setup_services(hass: HomeAssistant) -> None:
    """Registriert die Wortuhr Services in Home Assistant."""
    
    # Dynamische Animationsliste aus der const.py generieren
    animation_list = list(EVENT_ANIMATION_OPTIONS.keys())

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
        # 1. IP-Adresse automatisch über das gewählte Gerät ermitteln
        host = _get_host(hass, call)
        
        # 2. Text auslesen (Standard: leere Zeichenkette, falls nicht ausgefüllt)
        text = call.data.get("text", "")
        
        # 3. Euklidische Schätzung für den Color Picker
        color_id = 1 # Standardwert 
        if "rgb_color" in call.data:
            requested_rgb = call.data["rgb_color"]
            color_name, matched_id, _ = WortuhrColorMapper.find_closest_color(requested_rgb)
            color_id = matched_id
            _LOGGER.info(
                "Service show_event: RGB %s gematcht auf Farbe: %s (API ID: %s)", 
                requested_rgb, color_name, color_id
            )

        # 4. API Request absenden
        await async_show_event(
            hass,
            host,
            text=text,
            color_id=color_id,
            audio_id=call.data.get("audio"),
            preani=call.data.get("preani"),
            postani=call.data.get("postani"),
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

    # Dynamisches Validierungs-Schema für das GUI-Dropdown
    SHOW_EVENT_SCHEMA = vol.Schema(
        {
            vol.Optional("device_id"): cv.string, # Wird von HA für das Target benötigt
            vol.Optional("text"): cv.string,
            vol.Optional("rgb_color"): vol.All(vol.ExactSequence([cv.uint8, cv.uint8, cv.uint8]), vol.Coerce(tuple)),
            vol.Optional("audio"): cv.positive_int,
            vol.Optional("preani"): vol.In(animation_list),
            vol.Optional("postani"): vol.In(animation_list),
        }
    )     

    hass.services.async_register(
        DOMAIN,
        "show_text",
        show_text
    )

    hass.services.async_register(
        DOMAIN,
        "show_event",
        show_event,
        schema=SHOW_EVENT_SCHEMA
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