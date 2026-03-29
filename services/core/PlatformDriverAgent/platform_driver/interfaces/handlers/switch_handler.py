from .base_handler import BaseHandler


class SwitchHandler(BaseHandler):

    def handle_write(self, api_client, register, value):
        entity_id = register.entity_id
        entity_point = register.entity_point

        if entity_point == "state":
            if value == 1:
                api_client.call_service("switch", "turn_on", {"entity_id": entity_id})
            elif value == 0:
                api_client.call_service("switch", "turn_off", {"entity_id": entity_id})
            else:
                raise ValueError("Switch state must be 0 or 1")

        else:
            raise ValueError(f"Unsupported switch attribute: {entity_point}")

    def handle_read(self, entity_data, register):
        entity_point = register.entity_point

        if entity_point == "state":
            state = entity_data.get("state", None)
            return 1 if state == "on" else 0

        return entity_data.get("attributes", {}).get(entity_point, 0)