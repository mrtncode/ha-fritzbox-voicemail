"""Adds config flow for FritzBox Voicemail."""

from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, CONF_URL
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant.loader import async_get_loaded_integration
from slugify import slugify

from custom_fritzconnection import FritzConnection
from .const import DOMAIN, LOGGER


class FritzBoxVoicemailFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for FritzBox Voicemail."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle a flow initialized by the user."""
        _errors = {}
        if user_input is not None:
            try:
                await self._test_credentials(
                    address=user_input[CONF_URL],
                    username=user_input[CONF_USERNAME],
                    password=user_input[CONF_PASSWORD],
                )
                return self.async_create_entry(
                    title="Fritz!Box " + user_input[CONF_USERNAME],
                    data=user_input,
                )
            except Exception as exception:
                LOGGER.warning(exception)
                _errors["base"] = "auth"
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_URL): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.URL,
                        ),
                    ),
                    vol.Required(
                        CONF_USERNAME,
                        default=(user_input or {}).get(CONF_USERNAME, vol.UNDEFINED),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT,
                        ),
                    ),
                    vol.Required(CONF_PASSWORD): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.PASSWORD,
                        ),
                    )
                }
            ),
            errors=_errors,
        )

    async def _test_credentials(self, address: str, username: str, password: str) -> None:
        """Validate credentials."""

        await self.hass.async_add_executor_job(
            lambda: FritzConnection(
                address=address,
                user=username,
                password=password,
            )
        )