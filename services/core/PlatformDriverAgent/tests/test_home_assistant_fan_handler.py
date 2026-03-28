# -*- coding: utf-8 -*- {{ {
# ===----------------------------------------------------------------------===
#
#                 Component of Eclipse VOLTTRON
#
# ===----------------------------------------------------------------------===
#
# Copyright 2023 Battelle Memorial Institute
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy
# of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#
# ===----------------------------------------------------------------------===
# }}}

from unittest.mock import Mock

import pytest

from platform_driver.interfaces.handlers.fan_handler import FanHandler


class _Register:
    def __init__(self, entity_id, entity_point):
        self.entity_id = entity_id
        self.entity_point = entity_point


@pytest.fixture
def fan_handler():
    return FanHandler()


@pytest.fixture
def api_client():
    return Mock()


@pytest.mark.parametrize("value,service", [(1, "turn_on"), (0, "turn_off")])
def test_handle_write_state_calls_expected_service(fan_handler, api_client, value, service):
    register = _Register("fan.living_room", "state")

    fan_handler.handle_write(api_client, register, value)

    api_client.call_service.assert_called_once_with("fan", service, {"entity_id": "fan.living_room"})


@pytest.mark.parametrize(
    "value,percentage",
    [
        (1, 33),
        (2, 66),
        (3, 100),
        ("low", 33),
        ("medium", 66),
        ("high", 100),
    ],
)
def test_handle_write_speed_maps_to_percentage(fan_handler, api_client, value, percentage):
    register = _Register("fan.living_room", "speed")

    fan_handler.handle_write(api_client, register, value)

    api_client.call_service.assert_called_once_with(
        "fan",
        "set_percentage",
        {"entity_id": "fan.living_room", "percentage": percentage},
    )


@pytest.mark.parametrize("value", [2, -1, "on", "invalid", None])
def test_handle_write_state_rejects_invalid_values(fan_handler, api_client, value):
    register = _Register("fan.living_room", "state")

    with pytest.raises(ValueError, match="Fan state must be 0 or 1"):
        fan_handler.handle_write(api_client, register, value)


@pytest.mark.parametrize("value", [0, 4, "max", "", None])
def test_handle_write_speed_rejects_invalid_values(fan_handler, api_client, value):
    register = _Register("fan.living_room", "speed")

    with pytest.raises(ValueError, match="Fan speed must be one of"):
        fan_handler.handle_write(api_client, register, value)


def test_handle_write_rejects_unsupported_entity_point(fan_handler, api_client):
    register = _Register("fan.living_room", "oscillation")

    with pytest.raises(ValueError, match="Unsupported fan attribute"):
        fan_handler.handle_write(api_client, register, 1)


@pytest.mark.parametrize("state,expected", [("on", 1), ("off", 0), ("unknown", 0), (None, 0)])
def test_handle_read_state_maps_to_int(fan_handler, state, expected):
    register = _Register("fan.living_room", "state")
    entity_data = {"state": state, "attributes": {}}

    assert fan_handler.handle_read(entity_data, register) == expected


@pytest.mark.parametrize(
    "percentage,expected",
    [
        (0, 1),
        (10, 1),
        (33, 1),
        (34, 2),
        (66, 2),
        (67, 3),
        (100, 3),
    ],
)
def test_handle_read_speed_maps_from_percentage(fan_handler, percentage, expected):
    register = _Register("fan.living_room", "speed")
    entity_data = {"state": "on", "attributes": {"percentage": percentage}}

    assert fan_handler.handle_read(entity_data, register) == expected


def test_handle_read_speed_defaults_to_low_when_percentage_missing(fan_handler):
    register = _Register("fan.living_room", "speed")
    entity_data = {"state": "on", "attributes": {}}

    assert fan_handler.handle_read(entity_data, register) == 1


def test_handle_read_speed_is_zero_when_fan_is_off(fan_handler):
    register = _Register("fan.living_room", "speed")
    entity_data = {"state": "off", "attributes": {}}

    assert fan_handler.handle_read(entity_data, register) == 0


def test_handle_read_fallback_to_attribute_value(fan_handler):
    register = _Register("fan.living_room", "preset_mode")
    entity_data = {"state": "on", "attributes": {"preset_mode": "eco"}}

    assert fan_handler.handle_read(entity_data, register) == "eco"