"""Switch platform for Fritzbox Voicemail."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_fritzconnection.lib.fritztam import FritzTAM
from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription

from .const import CONF_TAMS
from .entity import FritzboxVoicemailEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import FritzboxVoicemailDataUpdateCoordinator
    from .data import FritzboxVoicemailConfigEntry

ENTITY_DESCRIPTIONS = (
    SwitchEntityDescription(
        key="voicemail_enabled",
        name="Voicemail Enabled",
        icon="mdi:voicemail",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    entry: FritzboxVoicemailConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the switch platform."""
    async_add_entities(
        FritzboxVoicemailSwitch(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
            tam_index=tam["index"],
            tam_name=tam["name"],
        )
        for tam in entry.data.get(CONF_TAMS, [])
        for entity_description in ENTITY_DESCRIPTIONS
    )


class FritzboxVoicemailSwitch(FritzboxVoicemailEntity, SwitchEntity):
    """fritzbox_voicemail switch class."""

    def __init__(
        self,
        coordinator: FritzboxVoicemailDataUpdateCoordinator,
        entity_description: SwitchEntityDescription,
        tam_index: str,
        tam_name: str,
    ) -> None:
        """Initialize the switch class."""
        super().__init__(coordinator, tam_index=tam_index, tam_name=tam_name)
        self.entity_description = entity_description
        self._attr_unique_id = f"{self._attr_unique_id}_{entity_description.key}"
        self.fritz_connection = coordinator.config_entry.runtime_data.client
        self.tam = FritzTAM(fc=self.fritz_connection)

    @property
    def is_on(self) -> bool:
        """Return true if the switch is on."""
        selected_tam = next(
            (
                tam
                for tam in (self.coordinator.data or {}).get("tam_list", [])
                if str(tam["Index"]) == str(self.tam_index)
            ),
            None,
        )
        return selected_tam is not None and str(selected_tam.get("Enable")) == "1"

    async def async_turn_on(self) -> None:
        """Turn on the switch."""
        await self.hass.async_add_executor_job(
            lambda: self.tam.set_enable(tam_index=self.tam_index, enable=True)
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self) -> None:
        """Turn off the switch."""
        await self.hass.async_add_executor_job(
            lambda: self.tam.set_enable(tam_index=self.tam_index, enable=False)
        )
        await self.coordinator.async_request_refresh()
