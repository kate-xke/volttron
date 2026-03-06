class BaseHandler:
    """
    Base class for all domain handlers.
    """

    def handle_write(self, interface, register, value):
        raise NotImplementedError("Handler must implement handle_write()")
    