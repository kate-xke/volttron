from .base_handler import BaseHandler


class LightHandler(BaseHandler):

    def handle_write(self, interface, register, value):

        entity_id = register.entity_id
        entity_point = register.entity_point

        if entity_point == "state":

            if value == 1:
                interface.turn_on_lights(entity_id)

            elif value == 0:
                interface.turn_off_lights(entity_id)

            else:
                raise ValueError("Light state must be 0 or 1")

        elif entity_point == "brightness":

            if not (0 <= value <= 255):
                raise ValueError("Brightness must be between 0 and 255")

            interface.change_brightness(entity_id, value)

        else:
            raise ValueError(f"Unsupported light attribute: {entity_point}")
        