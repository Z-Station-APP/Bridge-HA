from homeassistant.components.http import HomeAssistantView
from homeassistant.helpers.entity_registry import async_get as get_entity_registry
from homeassistant.helpers.device_registry import async_get as get_device_registry

def name_to_ascii_numeric(name: str) -> int:
    return int("".join(str(ord(c)) for c in name))

ACTIONABLE_MAP = {
    "light": ["brightness", "color_temp", "hs_color", "rgb_color", "xy_color"],
    "cover": ["current_position", "position", "tilt_position"],
    "fan": ["percentage", "speed", "preset_mode"],
    "climate": [
        "temperature", "target_temp_low", "target_temp_high",
        "hvac_mode", "fan_mode", "swing_mode", "preset_mode"
    ],
    "media_player": ["volume_level", "is_volume_muted", "source", "sound_mode"],
    "humidifier": ["humidity", "mode"],
}

ACTIONABLE_DOMAINS = list(ACTIONABLE_MAP.keys())


def extract_action_values(domain, attributes):
    """Return only actionable attributes for the domain."""
    if domain not in ACTIONABLE_MAP:
        return None
    keys = ACTIONABLE_MAP[domain]
    action = {k: attributes[k] for k in keys if k in attributes}
    return action or None


class ZStationRefreshDevicesView(HomeAssistantView):
    url = "/api/zstation/refresh_devices"
    name = "api:zstation:refresh_devices"
    requires_auth = True

    def __init__(self, hass):
        self.hass = hass

    async def get(self, request):
        hass = self.hass
        ent_reg = get_entity_registry(hass)
        dev_reg = get_device_registry(hass)
        area_reg = hass.helpers.area_registry.async_get_registry()

        result = {}

        for entity_id, entity_entry in ent_reg.entities.items():
            state = hass.states.get(entity_id)
            if state is None:
                continue

            domain = entity_id.split(".")[0]
            result.setdefault(domain, [])

            attributes = state.attributes
            action_values = extract_action_values(domain, attributes)
            zone_name = None
            zone_id = None

            device = dev_reg.devices.get(entity_entry.device_id)
            if device and device.area_id:
                area = area_reg.async_get_area(device.area_id)
                if area:
                    zone_name = area.name
                    zone_id = name_to_ascii_numeric(area.name)
            result[domain].append({
                "entity_id": entity_id,
                "domain": domain,
                "value": state.state,
                "attributes": attributes,
                "action_values": action_values,
                "zone": zone_name,
                "zone_id": zone_id
            })

        return self.json(result)

