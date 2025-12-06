from homeassistant.components.http import HomeAssistantView


def name_to_ascii_numeric(name: str) -> int:
    """Convert zone name to numeric ASCII identifier."""
    return int("".join(str(ord(c)) for c in name))


class ZStationZonesView(HomeAssistantView):
    """Return Home Assistant area registry as Z-Station zones."""

    url = "/api/zstation/getzone"
    name = "api:zstation:getzone"
    requires_auth = True

    def __init__(self, hass):
        self.hass = hass

    async def get(self, request):
        """Handle GET request and return list of zones."""
        area_reg = self.hass.helpers.area_registry.async_get_registry()

        zones = [
            {
                "id": name_to_ascii_numeric(area.name),
                "name": area.name,
                "ha_id": area.id,
            }
            for area in area_reg.areas.values()
        ]

        # Optional but useful: tri alphabétique pour stabilité de l’API
        zones.sort(key=lambda z: z["name"].lower())

        return self.json(zones)

