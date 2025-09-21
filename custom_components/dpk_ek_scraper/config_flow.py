"""Adds config flow for Scraper."""

from __future__ import annotations

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
CONFIG_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): selector.TextSelector(),
    }
)
OPTIONS = vol.Schema(
    {
        vol.Required(CONF_ORIGIN, default=vol.UNDEFINED): str,
        vol.Required(CONF_DEST, default=vol.UNDEFINED): str,
        vol.Required(CONF_CLASS, default=vol.UNDEFINED): selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=FLIGHT_CLASS_OPTIONS,
                mode=selector.SelectSelectorMode.DROPDOWN,
            )
        ),
        vol.Required(CONF_DEPART, default=vol.UNDEFINED): selector.DateSelector(),
        vol.Required(CONF_RETURN, default=vol.UNDEFINED): selector.DateSelector(),
        vol.Required(CONF_MAX_LEGS, default=1): selector.NumberSelector(
            selector.NumberSelectorConfig(
                mode=selector.NumberSelectorMode.BOX,  # up/down arrows
                min=1,
                max=3,
                step=1,
            )
        ),
        vol.Required(CONF_MAX_DURATION, default=15): str,
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
    ) -> OptionsFlowHandler:
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None
    ) -> ConfigFlowResult:
        """Handle initial step."""
        if user_input:
            self.config = user_input
            if user_input[CONF_NAME] in configured_instances(self.hass):
                errors = {}
                errors[CONF_NAME] = "already_configured"
                return self.async_show_form(
                    step_id="user", data_schema=CONFIG_SCHEMA, errors=errors
                )

            return await self.async_step_init()
        return self.async_show_form(step_id="user", data_schema=CONFIG_SCHEMA)

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Show basic config for vertical blinds."""
        if user_input is not None:
            self.config.update(user_input)
            return await self.async_step_update()

        return self.async_show_form(
            step_id="init",
            data_schema=OPTIONS,
        )

    async def async_step_update(
        self,
        user_input: dict[str, Any] | None = None,  # noqa: ARG002
    ) -> ConfigFlowResult:
        """Create entry."""
        return self.async_create_entry(
            title=self.config[CONF_NAME],
            data={
                CONF_NAME: self.config[CONF_NAME],
            },
            options={
                CONF_ORIGIN: self.config.get(CONF_ORIGIN),
                CONF_DEST: self.config.get(CONF_DEST),
                CONF_DEPART: self.config.get(CONF_DEPART),
                CONF_RETURN: self.config.get(CONF_RETURN),
                CONF_MAX_LEGS: self.config.get(CONF_MAX_LEGS),
                CONF_MAX_DURATION: self.config.get(CONF_MAX_DURATION),
                CONF_CLASS: self.config.get(CONF_CLASS),
            },
        )


class OptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry
        self.current_config: dict = dict(config_entry.data)
        self.options = dict(config_entry.options)
        _LOGGER.debug("options=%s", self.options)

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Manage the options."""
        schema = OPTIONS
        if user_input is not None:
            self.options.update(user_input)
            return await self._update_options()
        return self.async_show_form(
            step_id="init",
            data_schema=self.add_suggested_values_to_schema(
                schema, user_input or self.options
            ),
        )

    async def _update_options(self) -> ConfigFlowResult:
        """Update config entry options."""
        return self.async_create_entry(title="", data=self.options)


class MyIntegrationOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow (modify settings after initial setup)."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options_schema = vol.Schema(
            {
                vol.Required(
                    CONF_ORIGIN,
                    default=self.config_entry.options.get(CONF_ORIGIN),
                ): str,
                vol.Required(
                    CONF_DEST,
                    default=self.config_entry.options.get(CONF_DEST),
                ): str,
                vol.Required(
                    CONF_DEPART,
                    default=self.config_entry.options.get(CONF_DEPART),
                ): selector.DateSelector(),
                vol.Required(
                    CONF_RETURN,
                    default=self.config_entry.options.get(CONF_RETURN),
                ): selector.DateSelector(),
                vol.Required(
                    CONF_MAX_LEGS,
                    default=self.config_entry.options.get(CONF_MAX_LEGS),
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
                    default=self.config_entry.options.get(CONF_MAX_DURATION),
                ): str,
                vol.Required(
                    CONF_CLASS,
                    default=self.config_entry.options.get(CONF_CLASS),
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=FLIGHT_CLASS_OPTIONS,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
            }
        )

        return self.async_show_form(step_id="init", data_schema=options_schema)
