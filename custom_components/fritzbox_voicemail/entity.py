"""Entity class for Fritzbox Voicemail."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, DOMAIN
from .coordinator import FritzboxVoicemailDataUpdateCoordinator


class FritzboxVoicemailEntity(
    CoordinatorEntity[FritzboxVoicemailDataUpdateCoordinator]
):
    """Fritzbox Voicemail entity class."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: FritzboxVoicemailDataUpdateCoordinator,
        tam_index: str,
        tam_name: str | None = None,
    ) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self.tam_index = tam_index
        name = tam_name or f"TAM {tam_index}"

        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_tam_{tam_index}"

        self._attr_device_info = DeviceInfo(
            identifiers={
                (
                    DOMAIN,
                    f"{coordinator.config_entry.entry_id}_tam_{tam_index}",
                ),
            },
            name=f"Fritz!Box Voicemail: {name}",
            via_device=(
                DOMAIN,
                coordinator.config_entry.entry_id,
            ),
        )
