# -*- coding: utf-8 -*- {{{
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


import random
from math import pi
import json
import sys
from platform_driver.interfaces import BaseInterface, BaseRegister, BasicRevert
from volttron.platform.agent import utils
from volttron.platform.vip.agent import Agent
import logging
import requests
from requests import get

from .handlers import LightHandler, ClimateHandler, GenericHandler, FanHandler
from .api_client import HomeAssistantAPIClient

_log = logging.getLogger(__name__)
type_mapping = {"string": str,
                "int": int,
                "integer": int,
                "float": float,
                "bool": bool,
                "boolean": bool}

service_mapping= {
    "light": LightHandler(),
    "climate": ClimateHandler(),
    "input_boolean": GenericHandler(),
    "fan": FanHandler(),
}

class HomeAssistantRegister(BaseRegister):
    def __init__(self, read_only, pointName, units, reg_type, attributes, entity_id, entity_point, default_value=None,
                 description=''):
        super(HomeAssistantRegister, self).__init__("byte", read_only, pointName, units, description='')
        self.reg_type = reg_type
        self.attributes = attributes
        self.entity_id = entity_id
        self.value = None
        self.entity_point = entity_point


class Interface(BasicRevert, BaseInterface):
    def __init__(self, **kwargs):
        super(Interface, self).__init__(**kwargs)
        self.api_client = None

    def configure(self, config_dict, registry_config_str):
        ip_address = config_dict.get("ip_address", None)
        access_token = config_dict.get("access_token", None)
        port = config_dict.get("port", None)

        if ip_address is None:
            raise ValueError("IP address is required.")
        if access_token is None:
            raise ValueError("Access token is required.")
        if port is None:
            raise ValueError("Port is required.")

        self.api_client = HomeAssistantAPIClient(ip_address, port, access_token)
        self.parse_config(registry_config_str)

    def get_point(self, point_name):
        register = self.get_register_by_name(point_name)
        entity_data = self.api_client.get_state(register.entity_id)

        domain = register.entity_id.split(".")[0]
        handler = service_mapping.get(domain, None)

        if handler:
            return handler.handle_read(entity_data, register)
        else:
            if register.entity_point == "state":
                return entity_data.get("state", None)
            else:
                return entity_data.get("attributes", {}).get(register.entity_point, 0)


    def _set_point(self, point_name, value):
        register = self.get_register_by_name(point_name)
        if register.read_only:
            raise IOError("Trying to write to a point configured read only: " + point_name)
        register.value = register.reg_type(value)

        domain = register.entity_id.split(".")[0]
        handler = service_mapping.get(domain, None)
        if handler is None:
            error_msg = (
                f"No handler found for domain: {domain}. "
                f"Supported domains: {list(service_mapping.keys())}"
            )
            _log.error(error_msg)
            raise ValueError(error_msg)

        handler.handle_write(self.api_client, register, register.value)
        return register.value

    def _scrape_all(self):
        result = {}
        read_registers = self.get_registers_by_type("byte", True)
        write_registers = self.get_registers_by_type("byte", False)

        for register in read_registers + write_registers:
            entity_id = register.entity_id
            try:
                entity_data = self.api_client.get_state(entity_id)
                domain = entity_id.split(".")[0]
                handler = service_mapping.get(domain, None)

                if handler:
                    value = handler.handle_read(entity_data, register)
                else:
                    _log.debug(f"No handler for domain '{domain}', using raw value")
                    if register.entity_point == "state":
                        value = entity_data.get("state", None)
                    else:
                        value = entity_data.get("attributes", {}).get(
                            register.entity_point, 0)

                register.value = value
                result[register.point_name] = value

            except Exception as e:
                _log.error(f"Error for entity_id {entity_id}: {e}")

        return result

    def parse_config(self, config_dict):

        if config_dict is None:
            return
        for regDef in config_dict:

            if not regDef['Entity ID']:
                continue

            read_only = str(regDef.get('Writable', '')).lower() != 'true'
            entity_id = regDef['Entity ID']
            entity_point = regDef['Entity Point']
            point_name = regDef['Volttron Point Name']
            units = regDef['Units']
            description = regDef.get('Notes', '')
            default_value = ("Starting Value")
            type_name = regDef.get("Type", 'string')
            reg_type = type_mapping.get(type_name, str)
            attributes = regDef.get('Attributes', {})
            register_type = HomeAssistantRegister

            register = register_type(
                read_only,
                point_name,
                units,
                reg_type,
                attributes,
                entity_id,
                entity_point,
                default_value=default_value,
                description=description)

            if default_value is not None:
                self.set_default(point_name, register.value)

            self.insert_register(register)
