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

CONF_TAMS = "tams"


class FritzBoxVoicemailFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for FritzBox Voicemail Hub."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._data: dict[str, Any] = {}
        self._available_tams: list[dict[str, Any]] = []
        self._reauth_entry: config_entries.ConfigEntry | None = None

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle initial step: get credentials and connection URL."""
        _errors: dict[str, str] = {}

        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_URL])
            self._abort_if_unique_id_configured()

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
        """Handle selection of multiple TAMs."""
        _errors: dict[str, str] = {}

        if user_input is not None:
            selected_indices = user_input[CONF_TAMS]

            selected_tams = [
                {"index": tam["Index"], "name": tam["Name"]}
                for tam in self._available_tams
                if str(tam["Index"]) in selected_indices
                or tam["Index"] in selected_indices
            ]

            final_data = {
                **self._data,
                CONF_TAMS: selected_tams,
            }

            displayed_url = (
                self._data[CONF_URL].replace("http://", "").replace("https://", "")
            )

            return self.async_create_entry(
                title=f"Fritz!Box ({displayed_url})",
                data=final_data,
            )

        tam_options = [
            selector.SelectOptionDict(
                value=str(tam["Index"]), label=f"{tam['Name']} (Index {tam['Index']})"
            )
            for tam in self._available_tams
        ]

        return self.async_show_form(
            step_id="tam_selection",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_TAMS,
                        default=[str(tam["Index"]) for tam in self._available_tams],
                    ): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=tam_options,
                            multiple=True,
                            mode=selector.SelectSelectorMode.DROPDOWN,
                        )
                    ),
                }
            ),
            errors=_errors,
        )

    async def async_step_reauth(
        self,
        entry_data: dict[str, Any],  # noqa: ARG002
    ) -> config_entries.ConfigFlowResult:
        """Handle translation from reauth alert to reauth form."""
        if not (entry_id := self.context.get("entry_id")):
            return self.async_abort(reason="unknown")

        self._reauth_entry = self.hass.config_entries.async_get_entry(entry_id)
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle reauthorization with updated password."""
        _errors: dict[str, str] = {}
        if not self._reauth_entry:
            return self.async_abort(reason="unknown")

        if user_input is not None:
            success, _ = await self._test_credentials_and_get_tams(
                address=self._reauth_entry.data[CONF_URL],
                username=self._reauth_entry.data[CONF_USERNAME],
                password=user_input[CONF_PASSWORD],
            )

            if success:
                new_data = {
                    **self._reauth_entry.data,
                    CONF_PASSWORD: user_input[CONF_PASSWORD],
                }

                self.hass.config_entries.async_update_entry(
                    self._reauth_entry, data=new_data
                )

                await self.hass.config_entries.async_reload(self._reauth_entry.entry_id)
                return self.async_abort(reason="reauth_successful")

            _errors["base"] = "auth"

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_PASSWORD): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.PASSWORD
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
        except Exception as exception:  # noqa: BLE001
            LOGGER.exception(
                "Unexpected error during authentication/TAM retrieval: %s", exception
            )
            return False, []
        else:
            return True, valid_tams
