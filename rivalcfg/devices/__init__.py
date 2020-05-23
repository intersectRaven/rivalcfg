"""This module provides access to the profile of each supported device.

Profile spec
------------

A profile is just a ``dict`` that contains information about one or more mouse.
There is one profile file in ``rivalcfg/devices/`` by mouse familly (the "Rival
100" and the "Rival 100 Dota 2 Edition" are mouse of the same familly).

Here is what a profile file looks like::

    from .. import usbhid

    profile = {

        # The name of the mouse familly
        "name": "SteelSeries Rival 100",

        # List of all devices of the familly
        "models": [{
            # The name of a specific device of the familly
            "name": "SteelSeries Rival 100",
            # The vendor ID of the USB device (should always be 0x1038)
            "vendor_id": 0x1038,
            # The product ID of the USB device
            "product_id": 0x1702,
            # The control endpoint of the device (probably 0)
            "endpoint": 0,
        }, {
            "name": "SteelSeries Rival 100 (Dell China)",
            "vendor_id": 0x1038,
            "product_id": 0x170a,
            "endpoint": 0,
            # A device can override default values defined in settings
            "override_defaults": {
                "color": "#FF0000",
            },
        }],

        # All available settings for the mice
        "settings": {

            # A setting of the mouse. The key name is important, it will
            # be used to generates the Mouse class API and in the CLI
            "polling_rate": {
                # A label that will be used in one day to build a GUI
                "label": "Polling rate",
                # A short description of the option. Used to generate the CLI
                # help (rivalcfg --help)
                "description": "Set polling rate (Hz)",
                # The name of the CLI options to change this setting.
                "cli": ["-p", "--polling-rate"],
                # The repport type (rivalcfg.usbhid.HID_REPORT_TYPE_OUTPUT most
                # of the time)
                "report_type": usbhid.HID_REPORT_TYPE_OUTPUT,
                # The command that should be sent to the USB device to update
                # this setting.
                "command": [0x04, 0x00],
                # The type of value supported by this setting.
                # See the `rivalcfg.handlers` documentation for more
                # information.
                "value_type": "choice",
                # This parameter is specific to the `choice` handler.
                # Look at its documentation for more information.
                "choices": {
                    125: 0x04,
                    250: 0x03,
                    500: 0x02,
                    1000: 0x01,
                },
                # The factory default value of this setting.
                "default": 1000,
            },

            "color": {
                "label": "LED color",
                "description": "Set the mouse backlight color",
                "cli": ["-c", "--color"],
                "report_type": usbhid.HID_REPORT_TYPE_OUTPUT,
                "command": [0x05, 0x00],
                "value_type": "rgbcolor",
                "default": "#FF1800"
            },

            # ...

        },

        # The command that allows to persist data in the internal memory
        # of the device
        "save_command": {
            "report_type": usbhid.HID_REPORT_TYPE_OUTPUT,
            "command": [0x09, 0x00],
        },

    }

At runtime, a separated profile will be generated for each device of a mouse
familly. The profiles will then look like this::

    {

        "name": "SteelSeries Rival 100 (Dell China)",
        "vendor_id": 0x1038,
        "product_id": 0x170a,
        "endpoint": 0,

        "settings": {
            # ...
        },

        "save_command": {
            #...
        },

    }


Module API
----------

.. data:: rivalcfg.devices.PROFILES

    Profiles of each supported devices::

       {
           (vendor_id, product_id): {
               # profile data ...
           },
       }
"""


import types

from . import rival100  # noqa: F401


PROFILES = None


class UnsupportedDevice(Exception):
    """Exception raised when the requested device is not supported by rivalcfg.
    """


def get_profile(vendor_id=0x1038, product_id=None):
    """Get the profile of the requested device.

    :param int vendor_id: The vendor id of the device (optional, by default
                          this is set to the SteelSeries vendor id
                          (``0x1038``)).
    :param int product_id: The product id of one of the supported device (e.g.
                           ``0x1702``).
    :raise UnsupportedDevice: The requested device is not supported by
                              rivalcfg.
    :rtype: dict

    >>> from rivalcfg import devices
    >>> devices.get_profile(vendor_id=0x1038, product_id=0x1702)
    {...'name': 'SteelSeries Rival 100'...}
    """
    if not product_id:
        raise ValueError("You must provide a product_id")
    profile_name = (vendor_id, product_id)
    if profile_name not in PROFILES:
        raise UnsupportedDevice(
                "The requested device is not supported (%s)" % profile_name)
    return PROFILES[profile_name]


def _generate_profiles():
    """List devices imported in the current module and generates a separated
    profile for each device variation.

    :rtype: dict
    """
    profiles = {}
    for item in [globals()[name] for name in globals()]:
        if not isinstance(item, types.ModuleType):
            continue
        if not hasattr(item, "profile"):
            continue
        for model in item.profile["models"]:
            profile = item.profile.copy()
            profile_name = (
                    model["vendor_id"],
                    model["product_id"])
            del profile["models"]
            for k, v in model.items():
                if k == "override_defaults":
                    continue
                profile[k] = v
            # TODO override_defaults
            profiles[profile_name] = profile
        return profiles


PROFILES = _generate_profiles()
