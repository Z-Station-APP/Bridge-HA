from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from .const import DOMAIN


class ZStationConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the config flow for Z-Station Bridge."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Initial step of the configuration."""
        if user_input is None:
            # Display the empty configuration form
            return self.async_show_form(step_id="user")

        # Create the entry with no configuration data
        return self.async_create_entry(
            title="Z-Station Bridge",
            data={}
        )

