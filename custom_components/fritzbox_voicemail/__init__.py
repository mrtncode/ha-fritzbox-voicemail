from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

from homeassistant.const import Platform
from homeassistant.loader import async_get_loaded_integration

from .const import DOMAIN, LOGGER
from .coordinator import FritzboxVoicemailDataUpdateCoordinator
from .data import FritzboxVoicemailConfigEntry, FritzboxVoicemailData
from .views import MailboxView
from custom_fritzconnection import FritzConnection
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, CONF_URL

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.SWITCH
]


async def async_setup(
    hass: HomeAssistant,
    config: dict,
) -> bool:
    """Set up integration."""

    hass.http.register_view(MailboxView(hass))

    return True


async def async_setup_entry(
    hass: HomeAssistant,
    entry: FritzboxVoicemailConfigEntry,
) -> bool:
    """Set up integration from config entry."""

    fritz_connection = await hass.async_add_executor_job(
        lambda: FritzConnection(
            address=entry.data[CONF_URL],
            user=entry.data[CONF_USERNAME],
            password=entry.data[CONF_PASSWORD]
        )
    )



    coordinator = FritzboxVoicemailDataUpdateCoordinator(
        hass,
        fritz_connection,
    )

    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = FritzboxVoicemailData(
        client=fritz_connection,
        coordinator=coordinator,
        integration=async_get_loaded_integration(
            hass,
            entry.domain,
        ),
    )

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.runtime_data

    hass.http.register_view(
        MailboxView(hass)
    )

    await hass.config_entries.async_forward_entry_setups(
        entry,
        PLATFORMS,
    )

    entry.async_on_unload(
        entry.add_update_listener(async_reload_entry)
    )

    return True

async def async_unload_entry(
    hass: HomeAssistant,
    entry: IntegrationBlueprintConfigEntry,
) -> bool:
    """Unload integration."""

    unload_ok = await hass.config_entries.async_unload_platforms(
        entry,
        PLATFORMS,
    )

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)

    return unload_ok


async def async_reload_entry(
    hass: HomeAssistant,
    entry: IntegrationBlueprintConfigEntry,
) -> None:
    """Reload integration."""

    await hass.config_entries.async_reload(entry.entry_id)