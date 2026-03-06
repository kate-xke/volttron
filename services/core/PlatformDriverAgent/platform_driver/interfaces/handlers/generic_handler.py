from .base_handler import BaseHandler


class GenericHandler(BaseHandler):

    def handle_write(self, interface, register, value):

        entity_id = register.entity_id
        entity_point = register.entity_point

        if entity_point != "state":
            raise ValueError(
                f"Generic handler only supports 'state', got {entity_point}"
            )

        if value == 1:
            interface.set_input_boolean(entity_id, "on")

        elif value == 0:
            interface.set_input_boolean(entity_id, "off")

        else:
            raise ValueError("State must be 0 or 1")
        