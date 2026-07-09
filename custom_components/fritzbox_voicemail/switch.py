"""Switch platform for integration_blueprint."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from .const import DOMAIN
from custom_components.fritzbox_voicemail.data import FritzboxVoicemailConfigEntry
from custom_fritzconnection.lib.fritztam import FritzTAM

from .entity import IntegrationBlueprintEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import FritzboxVoicemailDataUpdateCoordinator
    from .data import FritzboxVoicemailData

ENTITY_DESCRIPTIONS = (
    SwitchEntityDescription(
        key="voicemail_enabled",
        name="Voicemail Enabled",
        icon="mdi:voicemail",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: FritzboxVoicemailConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the switch platform."""
    async_add_entities(
        FritzboxVoicemailSwitch(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
            hass=hass,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class FritzboxVoicemailSwitch(IntegrationBlueprintEntity, SwitchEntity):
    """fritzbox_voicemail switch class."""

    def __init__(
        self,
        coordinator: FritzboxVoicemailDataUpdateCoordinator,
        entity_description: SwitchEntityDescription,
        hass: HomeAssistant,
    ) -> None:
        """Initialize the switch class."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self.hass = hass
        runtime_data = next(iter(self.hass.data[DOMAIN].values()))
        self.fritz_connection = runtime_data.client
        self.tam = FritzTAM(fc=self.fritz_connection)

    @property
    def is_on(self) -> bool:
        selected_tam = next(
            (
                tam
                for tam in self.coordinator.data["tam_list"]
                if tam["Index"] == "0"
            ),
            None,
        )
        return selected_tam is not None and selected_tam["Enable"] == "1"

    async def async_turn_on(self, **kwargs):
        await self.hass.async_add_executor_job(
            lambda: self.tam.set_enable(enable=True)
        )
        await self.coordinator.async_request_refresh()


    async def async_turn_off(self, **_: Any) -> None:
        """Turn off the switch."""
        await self.hass.async_add_executor_job(
            lambda: self.tam.set_enable(enable=False)
        )
        await self.coordinator.async_request_refresh()
