"""DataUpdateCoordinator for Fritzbox Voicemail."""

from __future__ import annotations

from datetime import timedelta
from typing import Any, TYPE_CHECKING

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from custom_fritzconnection.lib.fritztam import FritzTAM

from .const import DOMAIN, LOGGER

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from .data import FritzboxVoicemailConfigEntry
    from custom_fritzconnection.core.fritzconnection import FritzConnection


class FritzboxVoicemailDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Fritzbox voicemail data."""

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
            update_interval=timedelta(minutes=5),
        )

    async def _async_update_data(self) -> Any:
        """Fetch data from FritzBox."""

        try:
            return await self.hass.async_add_executor_job(
                self.tam.message_list
            )

        except Exception as err:
            raise UpdateFailed(
                f"Failed to update voicemail data: {err}"
            ) from err