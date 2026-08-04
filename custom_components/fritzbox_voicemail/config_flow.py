"""Config flow for FritzBox Voicemail."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from custom_fritzconnection import FritzConnection
from custom_fritzconnection.lib.fritztam import FritzTAM
from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_URL, CONF_USERNAME
from homeassistant.helpers import selector

from .const import DOMAIN, LOGGER

CONF_TAM_INDEX = "tam_index"
CONF_TAM_NAME = "tam_name"


class FritzBoxVoicemailFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for FritzBox Voicemail."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._data: dict[str, Any] = {}
        self._available_tams: list[dict[str, Any]] = []

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle initial step: get credentials and connection URL."""
        _errors: dict[str, str] = {}

        if user_input is not None:
            success, available_tams = await self._test_credentials_and_get_tams(
                address=user_input[CONF_URL],
                username=user_input[CONF_USERNAME],
                password=user_input[CONF_PASSWORD],
            )

            if success and available_tams:
                self._data = user_input
                self._available_tams = available_tams
                return await self.async_step_tam_selection()

            _errors["base"] = "auth" if not success else "no_tams_found"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_URL,
                        default=(user_input or {}).get(
                            CONF_URL, "http://192.168.178.1"
                        ),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(type=selector.TextSelectorType.URL)
                    ),
                    vol.Required(
                        CONF_USERNAME,
                        default=(user_input or {}).get(CONF_USERNAME, vol.UNDEFINED),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT)
                    ),
                    vol.Required(CONF_PASSWORD): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.PASSWORD
                        )
                    ),
                }
            ),
            errors=_errors,
        )

    async def async_step_tam_selection(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle selection of the specific TAM."""
        _errors: dict[str, str] = {}

        if user_input is not None:
            selected_tam_index = user_input[CONF_TAM_INDEX]
            selected_tam = next(
                (
                    tam
                    for tam in self._available_tams
                    if tam["Index"] == selected_tam_index
                ),
                None,
            )

            if selected_tam:
                final_data = {
                    **self._data,
                    CONF_TAM_INDEX: selected_tam["Index"],
                    CONF_TAM_NAME: selected_tam["Name"],
                }
                # Add TAM index to the entity id to ensure uniqueness
                await self.async_set_unique_id(
                    f"{self._data[CONF_URL]}_tam_{selected_tam['Index']}"
                )
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"Fritz!Box TAM: {selected_tam['Name']}",
                    data=final_data,
                )

        tam_options = [
            selector.SelectOptionDict(
                value=tam["Index"], label=f"{tam['Name']} (Index {tam['Index']})"
            )
            for tam in self._available_tams
        ]

        return self.async_show_form(
            step_id="tam_selection",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_TAM_INDEX): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=tam_options,
                            mode=selector.SelectSelectorMode.DROPDOWN,
                        )
                    ),
                }
            ),
            errors=_errors,
        )

    async def _test_credentials_and_get_tams(
        self, address: str, username: str, password: str
    ) -> tuple[bool, list[dict[str, Any]]]:
        """Validate credentials and fetch structured TAM list."""
        try:
            fritz = await self.hass.async_add_executor_job(
                lambda: FritzConnection(
                    address=address,
                    user=username,
                    password=password,
                )
            )
            tam = FritzTAM(fc=fritz)
            tams = await self.hass.async_add_executor_job(tam.tam_list)

            valid_tams = [
                tam_item for tam_item in tams if tam_item.get("Name") is not None
            ]
            return True, valid_tams
        except Exception as exception:  # noqa: BLE001
            LOGGER.exception(
                "Unexpected error during authentication/TAM retrieval: %s", exception
            )
            return False, []
