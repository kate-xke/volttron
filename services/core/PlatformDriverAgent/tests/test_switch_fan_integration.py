import json
import logging
import os
import pytest
import gevent

from volttron.platform.agent.known_identities import (
    PLATFORM_DRIVER,
    CONFIGURATION_STORE,
)
from volttron.platform import get_services_core
from volttron.platform.agent import utils
from volttrontesting.utils.platformwrapper import PlatformWrapper

utils.setup_logging()
logger = logging.getLogger(__name__)

HA_IP = os.getenv("HA_IP", "")
HA_TOKEN = os.getenv("HA_ACCESS_TOKEN", "")
HA_PORT = os.getenv("HA_PORT", "")

skip_msg = "HA connection not configured"
pytestmark = pytest.mark.skipif(
    not (HA_IP and HA_TOKEN and HA_PORT),
    reason=skip_msg
)

# ============================================================
# Switch Tests
# ============================================================

SWITCH_DEVICE_TOPIC = "devices/ha_switch"


def test_switch_get_point(volttron_instance, switch_config_store):
    """Read switch state — should be 0 (off) or 1 (on)."""
    agent = volttron_instance.dynamic_agent
    result = agent.vip.rpc.call(
        PLATFORM_DRIVER, 'get_point', 'ha_switch', 'switch_state'
    ).get(timeout=20)
    assert result in [0, 1]


def test_switch_scrape_all(volttron_instance, switch_config_store):
    """Scrape all switch points."""
    agent = volttron_instance.dynamic_agent
    result = agent.vip.rpc.call(
        PLATFORM_DRIVER, 'scrape_all', 'ha_switch'
    ).get(timeout=20)
    assert result in [{'switch_state': 0}, {'switch_state': 1}]


def test_switch_set_point(volttron_instance, switch_config_store):
    """Turn on switch, verify state changes to 1."""
    agent = volttron_instance.dynamic_agent
    agent.vip.rpc.call(
        PLATFORM_DRIVER, 'set_point', 'ha_switch', 'switch_state', 1
    )
    gevent.sleep(10)
    result = agent.vip.rpc.call(
        PLATFORM_DRIVER, 'scrape_all', 'ha_switch'
    ).get(timeout=20)
    assert result == {'switch_state': 1}


@pytest.fixture(scope="module")
def switch_config_store(volttron_instance, platform_driver):
    capabilities = [{"edit_config_store": {"identity": PLATFORM_DRIVER}}]
    volttron_instance.add_capabilities(
        volttron_instance.dynamic_agent.core.publickey, capabilities
    )

    registry_config = "switch_test.json"
    registry_obj = [{
        "Entity ID": "switch.volttrontest_switch",
        "Entity Point": "state",
        "Volttron Point Name": "switch_state",
        "Units": "On / Off",
        "Units Details": "off: 0, on: 1",
        "Writable": True,
        "Starting Value": 3,
        "Type": "int",
        "Notes": "integration test switch"
    }]

    volttron_instance.dynamic_agent.vip.rpc.call(
        CONFIGURATION_STORE, "manage_store", PLATFORM_DRIVER,
        registry_config, json.dumps(registry_obj), config_type="json"
    )
    gevent.sleep(2)

    driver_config = {
        "driver_config": {
            "ip_address": HA_IP,
            "access_token": HA_TOKEN,
            "port": HA_PORT,
        },
        "driver_type": "home_assistant",
        "registry_config": f"config://{registry_config}",
        "timezone": "US/Pacific",
        "interval": 30,
    }

    volttron_instance.dynamic_agent.vip.rpc.call(
        CONFIGURATION_STORE, "manage_store", PLATFORM_DRIVER,
        SWITCH_DEVICE_TOPIC, json.dumps(driver_config), config_type="json"
    )
    gevent.sleep(2)
    yield platform_driver

    volttron_instance.dynamic_agent.vip.rpc.call(
        CONFIGURATION_STORE, "manage_delete_store", PLATFORM_DRIVER
    )
    gevent.sleep(0.1)


# ============================================================
# Fan Tests
# ============================================================

FAN_DEVICE_TOPIC = "devices/ha_fan"


def test_fan_get_point(volttron_instance, fan_config_store):
    """Read fan state — should be 0 (off) or 1 (on)."""
    agent = volttron_instance.dynamic_agent
    result = agent.vip.rpc.call(
        PLATFORM_DRIVER, 'get_point', 'ha_fan', 'fan_state'
    ).get(timeout=20)
    assert result in [0, 1]


def test_fan_scrape_all(volttron_instance, fan_config_store):
    """Scrape all fan points — state and speed."""
    agent = volttron_instance.dynamic_agent
    result = agent.vip.rpc.call(
        PLATFORM_DRIVER, 'scrape_all', 'ha_fan'
    ).get(timeout=20)
    assert 'fan_state' in result
    assert 'fan_speed' in result
    assert result['fan_state'] in [0, 1]


def test_fan_set_state(volttron_instance, fan_config_store):
    """Turn on fan, verify state changes to 1."""
    agent = volttron_instance.dynamic_agent
    agent.vip.rpc.call(
        PLATFORM_DRIVER, 'set_point', 'ha_fan', 'fan_state', 1
    )
    gevent.sleep(10)
    result = agent.vip.rpc.call(
        PLATFORM_DRIVER, 'get_point', 'ha_fan', 'fan_state'
    ).get(timeout=20)
    assert result == 1


def test_fan_set_speed(volttron_instance, fan_config_store):
    """Set fan speed to 2 (medium/66%), verify read back."""
    agent = volttron_instance.dynamic_agent
    # Make sure fan is on first
    agent.vip.rpc.call(
        PLATFORM_DRIVER, 'set_point', 'ha_fan', 'fan_state', 1
    )
    gevent.sleep(5)
    # Set speed
    agent.vip.rpc.call(
        PLATFORM_DRIVER, 'set_point', 'ha_fan', 'fan_speed', 2
    )
    gevent.sleep(10)
    result = agent.vip.rpc.call(
        PLATFORM_DRIVER, 'get_point', 'ha_fan', 'fan_speed'
    ).get(timeout=20)
    assert result == 2


@pytest.fixture(scope="module")
def fan_config_store(volttron_instance, platform_driver):
    capabilities = [{"edit_config_store": {"identity": PLATFORM_DRIVER}}]
    volttron_instance.add_capabilities(
        volttron_instance.dynamic_agent.core.publickey, capabilities
    )

    registry_config = "fan_test.json"
    registry_obj = [
        {
            "Entity ID": "fan.volttrontest_fan",
            "Entity Point": "state",
            "Volttron Point Name": "fan_state",
            "Units": "On / Off",
            "Units Details": "off: 0, on: 1",
            "Writable": True,
            "Starting Value": 3,
            "Type": "int",
            "Notes": "integration test fan state"
        },
        {
            "Entity ID": "fan.volttrontest_fan",
            "Entity Point": "speed",
            "Volttron Point Name": "fan_speed",
            "Units": "speed level",
            "Units Details": "1: low, 2: medium, 3: high",
            "Writable": True,
            "Starting Value": 0,
            "Type": "int",
            "Notes": "integration test fan speed"
        }
    ]

    volttron_instance.dynamic_agent.vip.rpc.call(
        CONFIGURATION_STORE, "manage_store", PLATFORM_DRIVER,
        registry_config, json.dumps(registry_obj), config_type="json"
    )
    gevent.sleep(2)

    driver_config = {
        "driver_config": {
            "ip_address": HA_IP,
            "access_token": HA_TOKEN,
            "port": HA_PORT,
        },
        "driver_type": "home_assistant",
        "registry_config": f"config://{registry_config}",
        "timezone": "US/Pacific",
        "interval": 30,
    }

    volttron_instance.dynamic_agent.vip.rpc.call(
        CONFIGURATION_STORE, "manage_store", PLATFORM_DRIVER,
        FAN_DEVICE_TOPIC, json.dumps(driver_config), config_type="json"
    )
    gevent.sleep(2)
    yield platform_driver

    volttron_instance.dynamic_agent.vip.rpc.call(
        CONFIGURATION_STORE, "manage_delete_store", PLATFORM_DRIVER
    )
    gevent.sleep(0.1)


# ============================================================
# Shared Fixture
# ============================================================

@pytest.fixture(scope="module")
def platform_driver(volttron_instance):
    platform_uuid = volttron_instance.install_agent(
        agent_dir=get_services_core("PlatformDriverAgent"),
        config_file={
            "publish_breadth_first_all": False,
            "publish_depth_first": False,
            "publish_breadth_first": False,
        },
        start=True,
    )
    gevent.sleep(2)
    assert volttron_instance.is_agent_running(platform_uuid)
    yield platform_uuid

    volttron_instance.stop_agent(platform_uuid)
    if not volttron_instance.debug_mode:
        volttron_instance.remove_agent(platform_uuid)