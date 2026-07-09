from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.notify import NotifyEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .services import async_show_text

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities,
) -> None:
    """Set up the Wortuhr notify platform from a config entry."""
    async_add_entities([WortuhrNotificationEntity(hass, entry)], True)


class WortuhrNotificationEntity(NotifyEntity):
    """Notify entity that forwards messages to the Wortuhr show_text endpoint."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self._entry = entry
        self._host = entry.data.get(CONF_HOST, "")
        self._attr_name = "Wortuhr"
        self._attr_unique_id = f"{DOMAIN}_{entry.entry_id}_notify"

    @property
    def available(self) -> bool:
        return bool(self._host)

    @property
    def device_info(self) -> dict[str, Any]:
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "name": "Wortuhr",
            "manufacturer": "Wortuhr",
        }

    async def async_send_message(
        self,
        message: str,
        title: str | None = None,
        data: dict[str, Any] | None = None,
    ) -> None:
        """Send a message to the Wortuhr display."""
        if not message:
            return

        text = f"{title}: {message}" if title else message
        color = 0
        buzzer = 0

        if data:
            color = data.get("color", 0)
            buzzer = data.get("buzzer", 0)

        await async_show_text(self.hass, self._host, text, color, buzzer)
