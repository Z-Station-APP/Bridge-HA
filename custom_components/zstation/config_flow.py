from homeassistant import config_entries
from .const import DOMAIN

class ZStationConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the config flow for Z-Station Bridge."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Create a config entry without user input."""
        return self.async_create_entry(title="Z-Station", data={})



