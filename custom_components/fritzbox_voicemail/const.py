"""Constants for integration_blueprint."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "fritzbox_voicemail"
ATTRIBUTION = "Data provided by FritzBox"

CONF_TAM_NAME = "tam_name"
CONF_TAM_INDEX = "tam_index"