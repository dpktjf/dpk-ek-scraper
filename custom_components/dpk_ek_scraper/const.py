"""Constants for eto_irrigation."""

from datetime import timedelta
from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "dpk_ek_scraper"
ATTRIBUTION = "DPK"
MANUFACTURER = "DPK"
CONFIG_FLOW_VERSION = 1

DEFAULT_NAME = "EK Scraper"
DEFAULT_RETRY = 60
UPDATE_INTERVAL = timedelta(minutes=1)
# UPDATE_INTERVAL = timedelta(hours=6)

# ek
CONF_ORIGIN = "origin"
CONF_DEST = "destination"
CONF_DEPART = "departure_date"
CONF_RETURN = "return_date"
CONF_MAX_LEGS = "max_legs"
CONF_MAX_DURATION = "max_duration"
CONF_CLASS = "class"

CONF_MONTH = "month"
CONF_YEAR = "year"
CONF_DAYS = "days_to_scrape"


ATTR_STATUS = "reward_status"
ATTR_UPPER = "upper"
ATTR_PREMIUM = "premium"
ATTR_ECONOMY = "economy"
ATTR_STATUS = "status"
ATTR_CODE = "code"
ATTR_MSG = "message"
ATTR_PTS = "pts"
ATTR_SAVER = "saver"
