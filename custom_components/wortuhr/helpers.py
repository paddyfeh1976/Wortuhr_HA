"""Helper functions for the Wortuhr integration."""
from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from .const import DOMAIN


def async_get_entity_id_by_unique_id(
    hass: HomeAssistant, 
    platform: str, 
    unique_id: str
) -> str | None:
    """Sucht die echte aktuelle Entity-ID anhand der Unique-ID im Entity Registry."""
    registry = er.async_get(hass)
    return registry.async_get_entity_id(platform, DOMAIN, unique_id)