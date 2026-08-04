"""Adds config flow for FritzBox Voicemail."""

from __future__ import annotations

import voluptuous as vol
from custom_fritzconnection import FritzConnection
from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_URL, CONF_USERNAME
from homeassistant.helpers import selector

from custom_fritzconnection.lib.fritztam import FritzTAM

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
                success, available_tams = await self._test_credentials_and_get_tams(
                    address=user_input[CONF_URL],
                    username=user_input[CONF_USERNAME],
                    password=user_input[CONF_PASSWORD],
                )
                if success:
                    return await self._async_step_tam_selection(
                        user_input=user_input, available_tams=available_tams
                    )
                else:
                    _errors["base"] = "auth"
            except Exception as exception:  # noqa: BLE001
                LOGGER.exception("Unexpected error during auth: %s", exception)
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
                    ),
                }
            ),
            errors=_errors,
        )
    async def _async_step_tam_selection(
        self, user_input: dict | None = None, available_tams: list[str] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the TAM selection step."""
        _errors = {}
        if user_input is not None:
            try:
                return self.async_create_entry(
                    title="Fritz!Box " + user_input[CONF_USERNAME],
                    data=user_input,
                )
            except Exception as exception:  # noqa: BLE001
                LOGGER.exception("Unexpected error during auth: %s", exception)
                _errors["base"] = "auth"
        return self.async_show_form(
            step_id="tam_selection",
            data_schema=vol.Schema(
                # dropdown to select the TAM from the list of available TAMs
                {
                    vol.Required(
                        CONF_USERNAME,
                        default=(user_input or {}).get(CONF_USERNAME, vol.UNDEFINED),
                    ): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=available_tams or ["TAM1"],
                            mode=selector.SelectSelectorMode.DROPDOWN,
                        ),
                    ),
                }
            ),
            errors=_errors,
    )

    async def _test_credentials_and_get_tams(
        self, address: str, username: str, password: str
    ) -> tuple[bool, list[str]]:
        """Validate credentials and get available TAMs."""
        try:
            fritz = await self.hass.async_add_executor_job(
                lambda: FritzConnection(
                    address=address,
                    user=username,
                    password=password,
                )
            )
            tam = FritzTAM(fc=fritz)

            tams = await self.hass.async_add_executor_job(
                lambda: tam.tam_list()
            )
            available_tams = [tam["Name"] for tam in tams if tam["Name"] is not None]
            print("tams", tams)
            print(f"Available TAMs: {available_tams}")
            return True, available_tams
        except Exception as exception:  # noqa: BLE001
            LOGGER.exception("Unexpected error during auth: %s", exception)
            return False, []