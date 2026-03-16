from .base_handler import BaseHandler


class GenericHandler(BaseHandler):
    
    def handle_write(self, api_client, register, value):
        entity_id = register.entity_id
        entity_point = register.entity_point

        if entity_point != "state":
            raise ValueError(f"Generic handler only supports 'state', got {entity_point}")

        if value == 1:
            api_client.call_service("input_boolean", "turn_on", {"entity_id": entity_id})
        elif value == 0:
            api_client.call_service("input_boolean", "turn_off", {"entity_id": entity_id})
        else:
            raise ValueError("State must be 0 or 1")
    
    def handle_read(self, entity_data, register):
        entity_point = register.entity_point

        if entity_point == "state":
            state = entity_data.get("state", None)
            return 1 if state == "on" else 0
        # Extensible to support other attributes in the future instead of hardcoding state
        else:
            return entity_data.get("attributes", {}).get(entity_point, 0)