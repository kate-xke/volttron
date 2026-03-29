from .base_handler import BaseHandler


class FanHandler(BaseHandler):

    SPEED_TO_PERCENTAGE = {
        1: 33,
        2: 66,
        3: 100,
        "low": 33,
        "medium": 66,
        "high": 100,
    }

    def handle_write(self, api_client, register, value):
        entity_id = register.entity_id
        entity_point = register.entity_point

        if entity_point == "state":
            if value == 1:
                api_client.call_service("fan", "turn_on", {"entity_id": entity_id})
            elif value == 0:
                api_client.call_service("fan", "turn_off", {"entity_id": entity_id})
            else:
                raise ValueError("Fan state must be 0 or 1")

        elif entity_point == "speed":
            if value not in self.SPEED_TO_PERCENTAGE:
                raise ValueError("Fan speed must be one of: 1, 2, 3, low, medium, high")

            api_client.call_service("fan", "set_percentage", {
                "entity_id": entity_id,
                "percentage": self.SPEED_TO_PERCENTAGE[value],
            })

        else:
            raise ValueError(f"Unsupported fan attribute: {entity_point}")

    def handle_read(self, entity_data, register):
        entity_point = register.entity_point

        if entity_point == "state":
            state = entity_data.get("state", None)
            return 1 if state == "on" else 0

        if entity_point == "speed":
            state = entity_data.get("state", None)
            if state == "off":
                return 0

            percentage = entity_data.get("attributes", {}).get("percentage", None)
            if percentage is None:
                return 1
            if percentage <= 0:
                return 1
            if percentage <= 33:
                return 1
            if percentage <= 66:
                return 2
            return 3

        return entity_data.get("attributes", {}).get(entity_point, 0)