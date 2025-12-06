from homeassistant.components.http import HomeAssistantView
from homeassistant.helpers.entity_registry import async_get as get_entity_registry
from homeassistant.helpers.device_registry import async_get as get_device_registry

def name_to_ascii_numeric(name: str) -> int:
    return int("".join(str(ord(c)) for c in name))


# Mapping compact des attributs actionnables par domaine
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
    """Return only the relevant actionable attributes for the device."""
    if domain not in ACTIONABLE_MAP:
        return None

    keys = ACTIONABLE_MAP[domain]
    action = {k: attributes[k] for k in keys if k in attributes}

    return action or None


class ZStationDevicesView(HomeAssistantView):
    url = "/api/zstation/getdevices"
    name = "api:zstation:getdevices"
    requires_auth = True

    def __init__(self, hass):
        self.hass = hass

    async def get(self, request):
        hass = self.hass

        # Registries → récupérés une seule fois
        ent_reg = get_entity_registry(hass)
        dev_reg = get_device_registry(hass)
        area_reg = hass.helpers.area_registry.async_get_registry()

        result = {}

        for entity_id, entity_entry in ent_reg.entities.items():
            domain = entity_id.split(".")[0]
            state = hass.states.get(entity_id)

            # Initialise la liste du domaine
            result.setdefault(domain, [])

            # Sécurité si l'état n'existe plus
            if not state:
                name = entity_entry.original_name
                attributes = {}
                value = None
            else:
                name = state.name
                attributes = state.attributes
                value = state.state

            action_values = (
                extract_action_values(domain, attributes)
                if domain in ACTIONABLE_DOMAINS else None
            )

            # Récupération device + zone
            device = dev_reg.devices.get(entity_entry.device_id)
            device_info = None
            zone_name = None
            zone_id = None

            if device:
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

                if device.area_id:
                    area = area_reg.async_get_area(device.area_id)
                    if area:
                        zone_name = area.name
                        zone_id = name_to_ascii_numeric(area.name)

            # Construction finale
            result[domain].append({
                "id": entity_id,
                "domain": domain,
                "name": name,
                "value": value,
                "attributes": attributes,
                "action_values": action_values,
                "zone": zone_name,
                "zone_id": zone_id,
                "device_info": device_info
            })

        return self.json(result)

