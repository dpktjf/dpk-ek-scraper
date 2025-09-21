"""Adds config flow for Scraper."""

from __future__ import annotations

import datetime
import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.components.sensor.const import (
    DOMAIN as SENSOR_DOMAIN,
)
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)

# https://github.com/home-assistant/core/blob/master/homeassistant/const.py
from homeassistant.const import (
    CONF_NAME,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import selector

from .const import (
    CONF_CLASS,
    CONF_DEPART,
    CONF_DEST,
    CONF_MAX_DURATION,
    CONF_MAX_LEGS,
    CONF_ORIGIN,
    CONF_RETURN,
    CONFIG_FLOW_VERSION,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)
FLIGHT_CLASS_OPTIONS = ["economy", "premium", "business", "first"]
TODAY = datetime.datetime.now(tz=datetime.UTC).date().isoformat()
CONFIG_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): selector.TextSelector(),
    }
)
OPTIONS = vol.Schema(
    {
        vol.Required(CONF_ORIGIN, default="LON"): str,
        vol.Required(CONF_DEST, default="DXB"): str,
        vol.Required(CONF_CLASS, default="economy"): selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=FLIGHT_CLASS_OPTIONS,
                mode=selector.SelectSelectorMode.DROPDOWN,
            )
        ),
        vol.Required(CONF_DEPART, default=TODAY): selector.DateSelector(),
        vol.Required(CONF_RETURN, default=TODAY): selector.DateSelector(),
        vol.Required(CONF_MAX_LEGS, default=1): selector.NumberSelector(
            selector.NumberSelectorConfig(
                mode=selector.NumberSelectorMode.BOX,  # up/down arrows
                min=1,
                max=3,
                step=1,
            )
        ),
        vol.Required(CONF_MAX_DURATION, default=15.0): selector.NumberSelector(
            selector.NumberSelectorConfig(
                mode=selector.NumberSelectorMode.BOX,  # up/down arrows
                min=5.0,
                max=35.0,
                step=1.0,
            )
        ),
    }
)


@callback
def configured_instances(hass: HomeAssistant) -> set[str | None]:
    """Return a set of configured instances."""
    entries = [
        entry.data.get(CONF_NAME) for entry in hass.config_entries.async_entries(DOMAIN)
    ]
    return set(entries)


class ScraperConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Scraper."""

    VERSION = CONFIG_FLOW_VERSION

    def __init__(self) -> None:
        """Init method."""
        super().__init__()
        self.config: dict[str, Any] = {}

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> MyIntegrationOptionsFlowHandler:
        """Get the options flow for this handler."""
        return MyIntegrationOptionsFlowHandler(config_entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None
    ) -> ConfigFlowResult:
        errors = {}
        if user_input is not None:
            # Build a key tuple from user input
            new_key = (
                user_input[CONF_ORIGIN],
                user_input[CONF_DEST],
                user_input[CONF_CLASS],
                user_input[CONF_DEPART],
                user_input[CONF_RETURN],
            )

            # Iterate existing entries
            for entry in self._async_current_entries():
                existing_key = (
                    entry.data[CONF_ORIGIN],
                    entry.data[CONF_DEST],
                    entry.data[CONF_CLASS],
                    entry.data[CONF_DEPART],
                    entry.data[CONF_RETURN],
                )
                if new_key == existing_key:
                    errors["base"] = "already_configured"
                    break

            if not errors:
                return self.async_create_entry(
                    title=f"{user_input[CONF_ORIGIN]} → {user_input[CONF_DEST]}",
                    data=user_input,
                )

        return self.async_show_form(step_id="user", data_schema=OPTIONS, errors=errors)


class MyIntegrationOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow (modify settings after initial setup)."""

    def __init__(self, config_entry: config_entries.ConfigEntry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options_schema = vol.Schema(
            {
                vol.Required(
                    CONF_ORIGIN,
                    default=self.config_entry.options.get(
                        CONF_ORIGIN, self.config_entry.data.get(CONF_ORIGIN, "")
                    ),
                ): str,
                vol.Required(
                    CONF_DEST,
                    default=self.config_entry.options.get(
                        CONF_DEST, self.config_entry.data.get(CONF_DEST, "")
                    ),
                ): str,
                vol.Required(
                    CONF_CLASS,
                    default=self.config_entry.options.get(
                        CONF_CLASS, self.config_entry.data.get(CONF_CLASS, "")
                    ),
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=FLIGHT_CLASS_OPTIONS,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Required(
                    CONF_DEPART,
                    default=self.config_entry.options.get(
                        CONF_DEPART,
                        self.config_entry.data.get(
                            CONF_DEPART,
                            datetime.datetime.now(tz=datetime.UTC).date().isoformat(),
                        ),
                    ),
                ): selector.DateSelector(),
                vol.Required(
                    CONF_RETURN,
                    default=self.config_entry.options.get(
                        CONF_RETURN,
                        self.config_entry.data.get(
                            CONF_RETURN,
                            datetime.datetime.now(tz=datetime.UTC).date().isoformat(),
                        ),
                    ),
                ): selector.DateSelector(),
                vol.Required(
                    CONF_MAX_LEGS,
                    default=self.config_entry.options.get(
                        CONF_MAX_LEGS, self.config_entry.data.get(CONF_MAX_LEGS, 2)
                    ),
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        mode=selector.NumberSelectorMode.BOX,  # up/down arrows
                        min=1,
                        max=3,
                        step=1,
                    )
                ),
                vol.Required(
                    CONF_MAX_DURATION,
                    default=self.config_entry.options.get(
                        CONF_MAX_DURATION,
                        self.config_entry.data.get(CONF_MAX_DURATION, 15.0),
                    ),
                ): float,
            }
        )

        return self.async_show_form(step_id="init", data_schema=options_schema)
