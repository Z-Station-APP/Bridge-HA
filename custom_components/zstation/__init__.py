import logging
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigEntry
from homeassistant.core import HomeAssistant

from homeassistant.helpers import config_entry_oauth2_flow  

from .const import DOMAIN
from .zones_api import ZStationZonesView
from .devices_api import ZStationDevicesView
from .refresh_devices_api import ZStationRefreshDevicesView
from .execute_action_api import ZStationExecuteActionView

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict):
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):

    # ---------------------------
    # OAuth2 client
    # ---------------------------
    config_entry_oauth2_flow.async_register_implementation(
        hass,
        DOMAIN,
        config_entry_oauth2_flow.LocalOAuth2Implementation(
            hass,
            DOMAIN,
            "https://zstation-app.com/mobile", 
            "",                            
            "/auth/authorize",              
            "/auth/token",                  
        ),
    )
    
    _register_api_views(hass)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    return True


def _register_api_views(hass: HomeAssistant):
    hass.http.register_view(ZStationZonesView(hass))
    hass.http.register_view(ZStationDevicesView(hass))
    hass.http.register_view(ZStationRefreshDevicesView(hass))
    hass.http.register_view(ZStationExecuteActionView(hass))


class ZStationConfigFlow(ConfigFlow, domain=DOMAIN):

    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            return self.async_create_entry(title="Z-Station", data=user_input)
        return self.async_show_form(
            step_id="user", data_schema=vol.Schema({}), errors=errors
        )




