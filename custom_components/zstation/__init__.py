import logging
from homeassistant.config_entries import ConfigFlow, ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from .const import DOMAIN
from .zones_api import ZStationZonesView
from .devices_api import ZStationDevicesView
from .refresh_devices_api import ZStationRefreshDevicesView
from .execute_action_api import ZStationExecuteActionView

_LOGGER = logging.getLogger(__name__)
API_VIEWS_REGISTERED = False

async def async_setup(hass: HomeAssistant, config: dict):
    """YAML setup (unused)."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Z-Station from a config entry."""
    global API_VIEWS_REGISTERED
    if not API_VIEWS_REGISTERED:
        _register_api_views(hass)
        API_VIEWS_REGISTERED = True
    return True

def _register_api_views(hass: HomeAssistant):
    """Register API views for Z-Station."""
    hass.http.register_view(ZStationZonesView(hass))
    hass.http.register_view(ZStationDevicesView(hass))
    hass.http.register_view(ZStationRefreshDevicesView(hass))
    hass.http.register_view(ZStationExecuteActionView(hass))

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    return True

class ZStationConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Z-Station."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            return self.async_create_entry(title="Z-Station", data=user_input)
        return self.async_show_form(step_id="user", data_schema=vol.Schema({}))




