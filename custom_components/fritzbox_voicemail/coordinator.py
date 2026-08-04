"""DataUpdateCoordinator for Fritzbox Voicemail."""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, Any

from custom_fritzconnection.lib.fritztam import FritzTAM
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import DOMAIN, LOGGER

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

        for tam_info in tam_list:
            tam_idx = int(tam_info.get("Index", 0))
            try:
                messages = self.tam.message_list(tamIndex=str(tam_idx))
                for msg in messages:
                    msg["Tam"] = tam_idx
                    all_messages.append(msg)
            except Exception as err:  # noqa: BLE001
                LOGGER.warning("Could not fetch messages for TAM %s: %s", tam_idx, err)

        return {
            "tam_list": tam_list,
            "messages": all_messages,
        }

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from FritzBox."""
        try:
            data = await self.hass.async_add_executor_job(self._fetch_all_tam_data)

        except Exception as err:
            msg = f"Failed to update data from FritzBox: {err}"
            raise UpdateFailed(msg) from err

        else:
            return data
