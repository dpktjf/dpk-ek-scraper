"""Constants for eto_irrigation."""

from datetime import timedelta

DOMAIN = "dpk_ek_scraper"
ATTRIBUTION = "DPK"
MANUFACTURER = "DPK"
CONFIG_FLOW_VERSION = 1

DEFAULT_NAME = "EK Scraper"
UPDATE_INTERVAL = timedelta(hours=6)

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

ATTR_ORIGIN = "origin"
ATTR_ORIGIN_NAME = "origin_name"
ATTR_DEPARTURE_TIME = "departure_time"
ATTR_DESTINATION = "destination"
ATTR_DESTINATION_NAME = "destination_name"
ATTR_ARRIVAL_TIME = "arrival_time"
ATTR_DURATION = "duration"
ATTR_LEGS = "legs"

ATTR_OUTBOUND = "outbound"
ATTR_OUT_DEPART = "outbound_depart"
ATTR_OUT_ARRIVE = "outbound_arrive"
ATTR_OUT_DURATION = "outbound_duration"
ATTR_OUT_LEGS = "outbound_legs"
ATTR_OUT_PRICE = "outbound_price"
ATTR_RETURN = "return"
ATTR_RET_DEPART = "return_depart"
ATTR_RET_ARRIVE = "return_arrive"
ATTR_RET_DURATION = "return_duration"
ATTR_RET_LEGS = "return_legs"
ATTR_RET_PRICE = "return_price"
