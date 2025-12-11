import logging
from homeassistant.components.http import HomeAssistantView
from homeassistant.helpers import entity_registry as er, device_registry as dr, area_registry as ar

_LOGGER = logging.getLogger(__name__)

def name_to_ascii_numeric(name: str) -> str:
    return "".join(str(ord(c)) for c in name)

class ZStationRefreshDevicesView(HomeAssistantView):
    url = "/api/zstation/refresh_device"
    name = "api:zstation:refresh_device"
    requires_auth = True

    def __init__(self, hass):
        self.hass = hass

    async def get(self, request):
        _LOGGER.info("Receiving Refresh device for Z-Station")
        try:
            entity_registry = er.async_get(self.hass)
            device_registry = dr.async_get(self.hass)
            excluded_domains = ["update", "todo", "tts", "event", "person", "device_tracker"]
            result = {}

            for entity_id, entity_entry in entity_registry.entities.items():
                domain = entity_id.split(".")[0]
                if domain in excluded_domains:
                    continue

                state = self.hass.states.get(entity_id)
                if state is None or state.state is None:
                    continue

                attributes = dict(state.attributes)
                name = state.name
                value = state.state
                subtype = attributes.get("device_class", domain)

                if not entity_entry.device_id:
                    continue

                device = device_registry.devices.get(entity_entry.device_id)
                if not device:
                    continue

                device_id = device.id
                if device_id not in result:
                    result[device_id] = {
                        "channels": {}
                    }

                channel_key = f"{subtype}"
                result[device_id]["channels"][channel_key] = {
                    "id": device_id,
                    "subtype": subtype,
                    "value": value
                }

            _LOGGER.info("Successfully Refresh by API for Z-Station")
            return self.json(result)

        except Exception as e:
            _LOGGER.error(f"Error fetching devices: {e}", exc_info=True)
            response = {"status": "error", "message": str(e)}
            return self.json(response, status_code=500)esult)

