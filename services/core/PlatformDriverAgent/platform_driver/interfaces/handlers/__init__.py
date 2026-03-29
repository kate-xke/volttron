"""
Handler module for Home Assistant interface.

Provides device-specific handlers for processing write operations
to different entity types in Home Assistant.
"""

from .base_handler import BaseHandler
from .light_handler import LightHandler
from .climate_handler import ClimateHandler
from .generic_handler import GenericHandler
from .fan_handler import FanHandler

__all__ = [
    "BaseHandler",
    "LightHandler",
    "ClimateHandler",
    "GenericHandler",
    "FanHandler"
]
