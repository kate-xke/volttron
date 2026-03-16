class BaseHandler:
    """
    Base class for all domain handlers.
    """
    def handle_write(self, api_client, register, value):
        raise NotImplementedError("Handler must implement handle_write()")
    
    # Convert the value read from HA to Volttron format and return it
    def handle_read(self, entity_data, register):
        raise NotImplementedError("Handler must implement handle_read()")