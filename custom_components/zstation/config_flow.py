from homeassistant import config_entries
import voluptuous as vol

from .const import DOMAIN


class ZStationConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the config flow for Z-Station Bridge."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema({}),  # REQUIRED for UI
                errors=errors
            )
        return self.async_create_entry(
            title="Z-Station Bridge",
            data=user_input
        )


