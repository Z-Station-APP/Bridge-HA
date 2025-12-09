import logging
from homeassistant.components.http import HomeAssistantView
from homeassistant.core import ServiceCall
import json

_LOGGER = logging.getLogger(__name__)

class ZStationExecuteActionView(HomeAssistantView):
    url = "/api/zstation/execute_action"
    name = "api:zstation:execute_action"
    requires_auth = True

    def __init__(self, hass):
        self.hass = hass

    async def post(self, request):
        _LOGGER.info("Receiving request to /api/zstation/execute_action")
        try:
            data = await request.json()
            domain = data.get("domain")
            service = data.get("service")
            service_data = data.get("service_data", {})
            target = data.get("target", {})

            if not domain or not service:
                return self.json({"status": "error", "message": "Domain and service are required"}, status_code=400)

            await self.hass.services.async_call(domain, service, service_data, blocking=True, target=target)

            _LOGGER.info(f"Successfully executed action: {domain}.{service}")
            return self.json({"status": "ok", "message": f"Executed {domain}.{service}"})

        except json.JSONDecodeError:
            _LOGGER.error("Invalid JSON data received")
            return self.json({"status": "error", "message": "Invalid JSON data"}, status_code=400)

        except Exception as e:
            _LOGGER.error(f"Error executing action: {e}")
            return self.json({"status": "error", "message": str(e)}, status_code=500)

