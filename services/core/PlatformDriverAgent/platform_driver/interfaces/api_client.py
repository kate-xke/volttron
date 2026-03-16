import logging
import requests

_log = logging.getLogger(__name__)


class HomeAssistantAPIClient:
    """
    Thin HTTP wrapper for the Home Assistant REST API.
    Only two public methods: get_state() and call_service().
    """

    def __init__(self, ip_address, port, access_token):
        self.base_url = f"http://{ip_address}:{port}"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

    def get_state(self, entity_id):
        """GET /api/states/{entity_id} → returns full entity JSON"""
        url = f"{self.base_url}/api/states/{entity_id}"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        else:
            error_msg = (
                f"GET {url} failed with status {response.status_code}: "
                f"{response.text}"
            )
            _log.error(error_msg)
            raise Exception(error_msg)

    def call_service(self, domain, service, data):
        """POST /api/services/{domain}/{service} with JSON data"""
        url = f"{self.base_url}/api/services/{domain}/{service}"
        try:
            response = requests.post(url, headers=self.headers, json=data)
            if response.status_code == 200:
                _log.info(f"Success: {domain}/{service} for {data.get('entity_id', '')}")
            else:
                error_msg = (
                    f"POST {url} failed with status {response.status_code}: "
                    f"{response.text}"
                )
                _log.error(error_msg)
                raise Exception(error_msg)
        except requests.RequestException as e:
            error_msg = f"Request error for {domain}/{service}: {e}"
            _log.error(error_msg)
            raise Exception(error_msg)