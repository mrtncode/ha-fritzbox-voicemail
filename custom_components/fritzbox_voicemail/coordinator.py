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

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from FritzBox."""
        try:
            tam_list = await self.hass.async_add_executor_job(
                self.tam.tam_list,
            )

            messages = await self.hass.async_add_executor_job(
                self.tam.message_list,
            )

            return {
                "tam_list": tam_list,
                "messages": messages,
            }

        except Exception as err:
            raise UpdateFailed(f"Failed to update voicemail data: {err}") from err
