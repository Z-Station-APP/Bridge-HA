import logging
from homeassistant.components.http import HomeAssistantView
from homeassistant.helpers import entity_registry as er, device_registry as dr, area_registry as ar

_LOGGER = logging.getLogger(__name__)

def name_to_ascii_numeric(name: str) -> str:
    return "".join(str(ord(c)) for c in name)

class ZStationDevicesView(HomeAssistantView):
    url = "/api/zstation/get_device"
    name = "api:zstation:get_device"
    requires_auth = True

    def __init__(self, hass):
        self.hass = hass

    async def get(self, request):
        _LOGGER.info("Receiving Get Config for Z-Station")
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
                attributes = dict(state.attributes)
                name = state.name
                value = state.state
                if value is None:
                    continue

                zone_name = "Home Assistant" 
                zone_id = name_to_ascii_numeric(zone_name)
                device_info = None
                subtype = attributes.get("device_class", domain)

                if entity_entry.device_id:
                    device = device_registry.devices.get(entity_entry.device_id)
                    if device:
                        device_id = device.id
                        if device_id not in result:
                            result[device_id] = {
                                "device_info": {
                                    "manufacturer": device.manufacturer,
                                    "model": device.model,
                                    "sw_version": device.sw_version,
                                    "hw_version": device.hw_version,
                                    "connections": list(device.connections),
                                    "identifiers": list(device.identifiers),
                                },
                                "channels": {}
                            }
                        if device.area_id:
                            area = area_registry.areas.get(device.area_id)
                            if area:
                                zone_name = area.name
                                zone_id = name_to_ascii_numeric(area.name)

                        channel_key = f"{subtype}"
                        result[device_id]["channels"][channel_key] = {
                            "id": device_id,
                            "type": domain,
                            "subtype": subtype,
                            "name": name,
                            "zone_id": zone_id,
                            "zone": zone_name,
                            "value": value,
                            "attributes": attributes
                        }

            _LOGGER.info("Successfully Get Config by API for Z-Station")
            return self.json(result)

        except Exception as e:
            _LOGGER.error(f"Error fetching devices: {e}")
            response = {"status": "error", "message": str(e)}
            return self.json(response, status_code=500)

