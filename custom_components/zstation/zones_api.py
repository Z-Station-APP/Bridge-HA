import logging
from homeassistant.components.http import HomeAssistantView
from homeassistant.helpers import area_registry as ar

_LOGGER = logging.getLogger(__name__)

def name_to_ascii_numeric(name: str) -> str:
    return "".join(str(ord(c)) for c in name)

class ZStationZonesView(HomeAssistantView):
    url = "/api/zstation/getzone"
    name = "api:zstation:getzone"
    requires_auth = True

    def __init__(self, hass):
        self.hass = hass

    async def get(self, request):
        _LOGGER.info("Receiving Get Zone by Z-Station")
        try:
            area_registry = ar.async_get(self.hass)
            zones = []

            for area_id, area in area_registry.areas.items():
                zones.append({
                    "id": name_to_ascii_numeric(area.name),
                    "name": area.name
                })

            _LOGGER.info("Successfully export zones")
            return self.json(zones)

        except Exception as e:
            _LOGGER.error(f"Error fetching zones: {e}")
            response = {"status": "error", "message": str(e)}
            return self.json(response, status_code=500)

