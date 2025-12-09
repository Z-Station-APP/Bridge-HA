import logging
from homeassistant.components.http import HomeAssistantView
from homeassistant.helpers import entity_registry as er, device_registry as dr
from homeassistant.helpers import area_registry as ar

_LOGGER = logging.getLogger(__name__)

def name_to_ascii_numeric(name: str) -> str:
    return "".join(str(ord(c)) for c in name)

class ZStationDevicesView(HomeAssistantView):
    url = "/api/zstation/getdevices"
    name = "api:zstation:getdevices"
    requires_auth = True

    def __init__(self, hass):
        self.hass = hass

    async def get(self, request):
        _LOGGER.info("Receiving request to /api/zstation/getdevices")
        try:
            entity_registry = er.async_get(self.hass)
            device_registry = dr.async_get(self.hass)
            area_registry = ar.async_get(self.hass)

            excluded_domains = ["update", "todo", "tts", "event", "person", "device_tracker"] 
            result = {}

            for entity_id, entity_entry in entity_registry.entities.items():
                domain = entity_id.split(".")[0]
                if domain in excluded_domains:  
                    continue

                state = self.hass.states.get(entity_id)
                if state is None:
                    continue
                if domain not in result:
                    result[domain] = []
                attributes = state.attributes
                name = state.name
                value = state.state

                zone_name = None
                zone_id = None
                device_info = None

                if entity_entry.device_id:
                    device = device_registry.devices.get(entity_entry.device_id)
                    if device and device.area_id:
                        device_info = {
                            "device_id": device.id,
                            "name": device.name,
                            "manufacturer": device.manufacturer,
                            "model": device.model,
                            "sw_version": device.sw_version,
                            "hw_version": device.hw_version,
                            "connections": list(device.connections),
                            "identifiers": list(device.identifiers),
                        }
                        area = area_registry.areas.get(device.area_id)
                        if area:
                            zone_name = area.name
                            zone_id = name_to_ascii_numeric(area.name)
                if zone_name is not None:
                    result[domain].append({
                        "id": entity_id,
                        "domain": domain,
                        "name": name,
                        "value": value,
                        "attributes": attributes,
                        "zone": zone_name,
                        "zone_id": zone_id,
                        "device_info": device_info
                    })

            _LOGGER.info("Successfully Get devices")
            return self.json(result)

        except Exception as e:
            _LOGGER.error(f"Error fetching devices: {e}")
            response = {"status": "error", "message": str(e)}
            return self.json(response, status_code=500)

        return self.json(result)

