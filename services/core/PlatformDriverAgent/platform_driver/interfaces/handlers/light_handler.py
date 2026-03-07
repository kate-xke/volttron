from .base_handler import BaseHandler


class LightHandler(BaseHandler):

    def handle_write(self, api_client, register, value):
        entity_id = register.entity_id
        entity_point = register.entity_point

        if entity_point == "state":
            if value == 1:
                api_client.call_service("light", "turn_on", {"entity_id": entity_id})
            elif value == 0:
                api_client.call_service("light", "turn_off", {"entity_id": entity_id})
            else:
                raise ValueError("Light state must be 0 or 1")

        elif entity_point == "brightness":
            if not (0 <= value <= 255):
                raise ValueError("Brightness must be between 0 and 255")
            api_client.call_service("light", "turn_on", {
                "entity_id": entity_id,
                "brightness": value,
            })

        else:
            raise ValueError(f"Unsupported light attribute: {entity_point}")
    
    def handle_read(self, entity_data, register):
        entity_point = register.entity_point

        if entity_point == "state":
            state = entity_data.get("state", None)
            return 1 if state == "on" else 0
        
        # For brightness, we assume it's stored in the attributes of the entity data
        # Extensible to support other attributes in the future instead of hardcoding brightness
        else:
            return entity_data.get("attributes", {}).get(entity_point, 0)
        