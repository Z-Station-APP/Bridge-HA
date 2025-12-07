from homeassistant.components.http import HomeAssistantView
from homeassistant.exceptions import HomeAssistantError
import logging

_LOGGER = logging.getLogger(__name__)

class ZStationExecuteActionView(HomeAssistantView):
    """Handle execution of HA services through Z-Station Bridge."""

    url = "/api/zstation/execute_action"
    name = "api:zstation:execute_action"
    requires_auth = True

    def __init__(self, hass):
        self.hass = hass

    async def post(self, request):
        """Execute a Home Assistant service call."""
        try:
            body = await request.json()
        except Exception:
            return self.json({"error": "Invalid JSON body"}, status=400)

        entity_id = body.get("entity_id")
        service = body.get("service")
        data = body.get("data", {})

        # Validate required fields
        if not entity_id or not service:
            return self.json(
                {"error": "Fields 'entity_id' and 'service' are required"},
                status=400,
            )

        # Validate entity ID structure
        if "." not in entity_id:
            return self.json(
                {"error": "Invalid entity_id format. Expected 'domain.object'"},
                status=400,
            )

        domain = entity_id.split(".")[0]

        # Payload building
        payload = {"entity_id": entity_id}
        if isinstance(data, dict):
            payload.update(data)
        else:
            return self.json({"error": "'data' must be an object"}, status=400)

        # Execute the service call safely
        try:
            await self.hass.services.async_call(
                domain, service, payload, blocking=True
            )
        except HomeAssistantError as err:
            _LOGGER.error("Service call failed: %s", err)
            return self.json(
                {"error": f"Service call failed: {str(err)}"},
                status=500,
            )
        except Exception as err:
            _LOGGER.error("Unexpected error in execute_action: %s", err)
            return self.json(
                {"error": "Unexpected internal error", "details": str(err)},
                status=500,
            )

        # Success response
        return self.json(
            {
                "status": "ok",
                "executed": {
                    "domain": domain,
                    "service": service,
                    "entity_id": entity_id,
                }
            }
        )

