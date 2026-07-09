from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from .coordinator import FritzboxVoicemailDataUpdateCoordinator
    from custom_fritzconnection.core.fritzconnection import FritzConnection


type FritzboxVoicemailConfigEntry = ConfigEntry[FritzboxVoicemailData]


@dataclass
class FritzboxVoicemailData:
    """Data for the Fritzbox Voicemail integration."""

    client: FritzConnection
    coordinator: FritzboxVoicemailDataUpdateCoordinator
    integration: Integration