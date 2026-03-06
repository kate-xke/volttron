from .base_handler import BaseHandler


class ClimateHandler(BaseHandler):

    MODE_MAP = {
        0: "off",
        2: "heat",
        3: "cool",
        4: "auto",
    }

    def handle_write(self, interface, register, value):

        entity_id = register.entity_id
        entity_point = register.entity_point

        if entity_point == "state":

            if value not in self.MODE_MAP:
                raise ValueError("Climate state must be 0, 2, 3, or 4")

            mode = self.MODE_MAP[value]

            interface.change_thermostat_mode(entity_id, mode)

        elif entity_point == "temperature":

            interface.set_thermostat_temperature(entity_id, value)

        else:
            raise ValueError(
                f"Unsupported climate attribute: {entity_point}"
            )
        