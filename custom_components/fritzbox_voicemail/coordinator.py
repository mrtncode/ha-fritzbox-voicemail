"""DataUpdateCoordinator for Fritzbox Voicemail."""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, Any

from custom_fritzconnection.core.exceptions import (
    FritzConnectionException,
    FritzSecurityError,
)
from custom_fritzconnection.lib.fritztam import FritzTAM
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import CONF_TAMS, DOMAIN, LOGGER

if TYPE_CHECKING:
    from custom_fritzconnection.core.fritzconnection import FritzConnection
    from homeassistant.core import HomeAssistant

    from .data import FritzboxVoicemailConfigEntry


class FritzboxVoicemailDataUpdateCoordinator(DataUpdateCoordinator):
    """Manage fetching FritzBox voicemail data."""

    config_entry: FritzboxVoicemailConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        fritz_connection: FritzConnection,
    ) -> None:
        """Initialize coordinator."""
        self.tam = FritzTAM(fc=fritz_connection)

        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=1),
        )

    def _fetch_all_tam_data(self) -> dict[str, Any]:
        """Fetch TAM list and messages for all configured TAMs (multi-TAM support)."""
        tam_list = self.tam.tam_list()
        all_messages: list[dict[str, Any]] = []

        configured_tams = self.config_entry.data.get(CONF_TAMS, [])
        target_indices = [str(tam["index"]) for tam in configured_tams] or [
            str(t.get("Index", 0)) for t in tam_list
        ]

        for tam_idx in target_indices:
            try:
                messages = self.tam.message_list(tamIndex=str(tam_idx))
                for msg in messages:
                    msg["Tam"] = tam_idx
                    all_messages.append(msg)
            except FritzSecurityError:
                raise
            except Exception as err:  # noqa: BLE001
                LOGGER.warning("Could not fetch messages for TAM %s: %s", tam_idx, err)

        return {
            "tam_list": tam_list,
            "messages": all_messages,
        }

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from FritzBox."""
        try:
            return await self.hass.async_add_executor_job(self._fetch_all_tam_data)
        except FritzSecurityError as err:
            e = "Authentication failed while fetching data from FritzBox"
            raise ConfigEntryAuthFailed(e) from err
        except FritzConnectionException as err:
            e = f"Connection to FritzBox lost: {err}"
            raise UpdateFailed(e) from err
        except Exception as err:
            e = f"Unexpected error while fetching data from FritzBox: {err}"
            raise UpdateFailed(e) from err
