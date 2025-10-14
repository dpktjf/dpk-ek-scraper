"""Adds config flow for Scraper."""

from __future__ import annotations

import datetime
import logging
from typing import TYPE_CHECKING, Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.components.webhook import async_generate_id

# https://github.com/home-assistant/core/blob/master/homeassistant/const.py
from homeassistant.const import (
    CONF_NAME,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import selector

from custom_components.dpk_ek_scraper.config import ScraperConfig

from .const import (
    CONF_CLASS,
    CONF_DEPART,
    CONF_DEST,
    CONF_MAX_DURATION,
    CONF_MAX_LEGS,
    CONF_ORIGIN,
    CONF_RETURN,
    CONF_WEBHOOK,
    CONFIG_FLOW_VERSION,
    DOMAIN,
)

if TYPE_CHECKING:
    from homeassistant.config_entries import (
        ConfigEntry,
        ConfigFlowResult,
    )

_LOGGER = logging.getLogger(__name__)
FLIGHT_CLASS_OPTIONS = ["economy", "premium", "business", "first"]
TODAY = datetime.datetime.now(tz=datetime.UTC).date().isoformat()
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
                step=0.25,
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
        """
        Handle the initial step of the config flow for user input.

        Args:
            user_input: Optional dictionary containing user-provided configuration data.

        Returns:
            ConfigFlowResult: The result of the config flow step.

        """
        errors = {}
        if user_input is not None:
            # Build a key tuple from user input for uniquness check
            new_key = ScraperConfig(
                origin=user_input[CONF_ORIGIN],
                destination=user_input[CONF_DEST],
                departure_date=user_input[CONF_DEPART],
                return_date=user_input[CONF_RETURN],
                ticket_class=user_input[CONF_CLASS],
            )

            # Iterate existing entries
            for entry in self._async_current_entries():
                existing_key = ScraperConfig(
                    origin=entry.data[CONF_ORIGIN],
                    destination=entry.data[CONF_DEST],
                    departure_date=entry.data[CONF_DEPART],
                    return_date=entry.data[CONF_RETURN],
                    ticket_class=entry.data[CONF_CLASS],
                )
                if new_key.equals(existing_key):
                    errors["base"] = "already_configured"
                    break

            if not errors:
                depart = datetime.datetime.strptime(
                    user_input[CONF_DEPART], "%Y-%m-%d"
                ).replace(tzinfo=datetime.UTC)
                retrn = datetime.datetime.strptime(
                    user_input[CONF_RETURN], "%Y-%m-%d"
                ).replace(tzinfo=datetime.UTC)
                flight_str = f"{depart.strftime('%d-%b')} / {retrn.strftime('%d-%b')}"
                webhook_id = async_generate_id()
                _LOGGER.debug("Generated webhook ID: %s", webhook_id)
                return self.async_create_entry(
                    title=(
                        f"{user_input[CONF_ORIGIN]} → {user_input[CONF_DEST]} "
                        f"({user_input[CONF_CLASS]}) {flight_str}"
                    ),
                    # data items are immutable but options items can be changed
                    data={
                        CONF_WEBHOOK: webhook_id,
                        CONF_ORIGIN: user_input[CONF_ORIGIN],
                        CONF_DEST: user_input[CONF_DEST],
                        CONF_CLASS: user_input[CONF_CLASS],
                        CONF_DEPART: user_input[CONF_DEPART],
                        CONF_RETURN: user_input[CONF_RETURN],
                    },
                    options={
                        CONF_MAX_LEGS: user_input[CONF_MAX_LEGS],
                        CONF_MAX_DURATION: user_input[CONF_MAX_DURATION],
                    },
                )

        return self.async_show_form(step_id="user", data_schema=OPTIONS, errors=errors)


class MyIntegrationOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow (modify settings after initial setup)."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize the options flow handler with the given config entry."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """
        Handle the initial step of the options flow.

        Args:
            user_input: Optional dictionary containing user-provided options.

        Returns:
            ConfigFlowResult: The result of the options flow step.

        """
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options_schema = vol.Schema(
            {
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
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        mode=selector.NumberSelectorMode.BOX,  # up/down arrows
                        min=1.0,
                        max=35.0,
                        step=0.25,
                    )
                ),
            }
        )

        return self.async_show_form(step_id="init", data_schema=options_schema)
