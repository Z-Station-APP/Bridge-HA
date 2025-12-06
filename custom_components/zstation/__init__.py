import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN
from .zones_api import ZStationZonesView
from .get_devices_api import ZStationDevicesView
from .refresh_devices_api import ZStationRefreshDevicesView
from .execute_action_api import ZStationExecuteActionView

_LOGGER = logging.getLogger(__name__)

API_VIEWS_REGISTERED = False


async def async_setup(hass: HomeAssistant, config: dict):
    """YAML setup (unused)."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Initialize the Z-Station Bridge and register REST API endpoints."""
    global API_VIEWS_REGISTERED

    _LOGGER.info("Initializing Z-Station Bridge")

    if hass.http is None:
        _LOGGER.error("HTTP server not yet ready")
        raise ConfigEntryNotReady("HTTP server not ready")

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {}

    if not API_VIEWS_REGISTERED:
        _register_api_views(hass)
        API_VIEWS_REGISTERED = True
        _LOGGER.debug("Z-Station API endpoints registered")

    return True


def _register_api_views(hass: HomeAssistant):
    """Register all HTTP API routes for the integration."""
    views = [
        ZStationZonesView,
        ZStationDevicesView,
        ZStationRefreshDevicesView,
        ZStationExecuteActionView,
    ]

    for view in views:
        hass.http.register_view(view(hass))


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    hass.data[DOMAIN].pop(entry.entry_id, None)
    _LOGGER.debug("Z-Station Bridge entry unloaded")
    return True


