# -*- coding: utf-8 -*- {{{
# ===----------------------------------------------------------------------===
#
# Component of Eclipse VOLTTRON
#
# ===----------------------------------------------------------------------===
#
# Copyright 2023 Battelle Memorial Institute
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy
# of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
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

from platform_driver.interfaces.handlers.switch_handler import SwitchHandler


class _Register:
    def __init__(self, entity_id, entity_point):
        self.entity_id = entity_id
        self.entity_point = entity_point


@pytest.fixture
def switch_handler():
    return SwitchHandler()


@pytest.fixture
def api_client():
    return Mock()


@pytest.mark.parametrize("value,service", [(1, "turn_on"), (0, "turn_off")])
def test_handle_write_state_calls_expected_service(switch_handler, api_client, value, service):
    register = _Register("switch.living_room_outlet", "state")

    switch_handler.handle_write(api_client, register, value)

    api_client.call_service.assert_called_once_with("switch", service, {"entity_id": "switch.living_room_outlet"})


@pytest.mark.parametrize("value", [2, -1, "on", "invalid", None])
def test_handle_write_state_rejects_invalid_values(switch_handler, api_client, value):
    register = _Register("switch.living_room_outlet", "state")

    with pytest.raises(ValueError, match="Switch state must be 0 or 1"):
        switch_handler.handle_write(api_client, register, value)


def test_handle_write_rejects_unsupported_entity_point(switch_handler, api_client):
    register = _Register("switch.living_room_outlet", "power_consumption")

    with pytest.raises(ValueError, match="Unsupported switch attribute"):
        switch_handler.handle_write(api_client, register, 1)


@pytest.mark.parametrize("state,expected", [("on", 1), ("off", 0), ("unknown", 0), (None, 0)])
def test_handle_read_state_maps_to_int(switch_handler, state, expected):
    register = _Register("switch.living_room_outlet", "state")
    entity_data = {"state": state, "attributes": {}}

    assert switch_handler.handle_read(entity_data, register) == expected


def test_handle_read_fallback_to_attribute_value(switch_handler):
    register = _Register("switch.living_room_outlet", "friendly_name")
    entity_data = {"state": "on", "attributes": {"friendly_name": "Living Room Outlet"}}

    assert switch_handler.handle_read(entity_data, register) == "Living Room Outlet"