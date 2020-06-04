"""
This modules handles udev-related stuff on Linux. It contains function to
generate, check and update rules files.

.. NOTE::

   The functions of this module must only be used with udev-based Linux distro.
"""


from .version import VERSION
from .devices import PROFILES


#: Path to the udev rules file
UDEV_RULES_FILE_PATH = "/etc/udev/rules.d/99-steelseries-rival.rules"


def generate_udev_rules():
    """Generates the content of the udev rules file.

    :rtype: str
    """
    rules = "# Generated by rivalcfg v%s\n" % VERSION
    rules += "# Do not edit this file. It can be regenerated with the following command:\n"  # noqa
    rules += "# \n"
    rules += "#     rivalcfg --update-udev\n\n"

    for profile in PROFILES.values():
        rules += "# %s\n" % profile["name"]
        rules += "SUBSYSTEM==\"hidraw\", ATTRS{idVendor}==\"%04x\", ATTRS{idProduct}==\"%04x\", MODE=\"0666\"\n" % (  # noqa
                profile["vendor_id"], profile["product_id"])
        rules += "SUBSYSTEM==\"usb\", ATTRS{idVendor}==\"%04x\", ATTRS{idProduct}==\"%04x\", MODE=\"0666\"\n\n" % (  # noqa
                profile["vendor_id"], profile["product_id"])

    return rules


def write_udev_rules_file(path=UDEV_RULES_FILE_PATH):
    """Generates and write the udev rules file at the given place.

    :param str path: The path of the output file.

    :raise PermissionError: The user has not sufficient permissions to write
                            the file.
    """
    rules = generate_udev_rules()
    # TODO
    print(rules)  # FIXME
    with open(path, "w") as rules_file:
        rules_file.write(rules)


def trigger_udev():
    pass


def check_udev_rules(path=UDEV_RULES_FILE_PATH):
    pass
