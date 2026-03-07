from .base_handler import BaseHandler


class ClimateHandler(BaseHandler):

    # Reverse mapping for reading state back from HA to Volttron format
    STATE_TO_INT = {"off": 0, "heat": 2, "cool": 3, "auto": 4}

    MODE_MAP = {
        0: "off",
        2: "heat",
        3: "cool",
        4: "auto",
    }

    def handle_write(self, api_client, register, value):
        entity_id = register.entity_id
        entity_point = register.entity_point

        if entity_point == "state":
            if value not in self.MODE_MAP:
                raise ValueError("Climate state must be 0, 2, 3, or 4")
            mode = self.MODE_MAP[value]
            api_client.call_service("climate", "set_hvac_mode", {
                "entity_id": entity_id,
                "hvac_mode": mode,
            })

        elif entity_point == "temperature":
            api_client.call_service("climate", "set_temperature", {
                "entity_id": entity_id,
                "temperature": value,
            })

        else:
            raise ValueError(f"Unsupported climate attribute: {entity_point}")

    def handle_read(self, entity_data, register):
        entity_point = register.entity_point

        if entity_point == "state":
            state = entity_data.get("state", None)
            if state not in self.STATE_TO_INT:
                raise ValueError(f"Unsupported climate state: {state}")
            return self.STATE_TO_INT[state]
        # Extensible to support other attributes in the future instead of hardcoding temperature and other attributes
        else:
            return entity_data.get("attributes", {}).get(entity_point, 0)  