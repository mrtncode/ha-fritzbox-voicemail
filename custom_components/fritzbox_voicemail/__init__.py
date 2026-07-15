from __future__ import annotations

from typing import TYPE_CHECKING

import voluptuous as vol
from homeassistant.const import CONF_PASSWORD, CONF_URL, CONF_USERNAME, Platform
from homeassistant.exceptions import HomeAssistantError
from homeassistant.const import Platform
from homeassistant.loader import async_get_loaded_integration
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN
from .coordinator import FritzboxVoicemailDataUpdateCoordinator
from .data import FritzboxVoicemailConfigEntry, FritzboxVoicemailData
from .views import MailboxView
from custom_fritzconnection import FritzConnection
from custom_fritzconnection.lib.fritztam import FritzTAM

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.SWITCH
]

CONFIG_SCHEMA = cv.empty_config_schema(DOMAIN)

SERVICE_DELETE_VOICEMAIL_MESSAGE = "delete_voicemail_message"

SERVICE_SCHEMA = vol.Schema(
    {
        vol.Required("delete_mode"): vol.In(["all", "specific"]),
        vol.Optional("message_index"): cv.positive_int,
    }
)


async def async_delete_voicemail_message(
    hass: HomeAssistant,
    service_call,
) -> None:
    """Delete voicemail messages from the FritzBox."""

    runtime_data = next(iter(hass.data.get(DOMAIN, {}).values()), None)

    if runtime_data is None:
        raise HomeAssistantError("FritzBox Voicemail is not set up")

    fritz_connection = runtime_data.client
    tam = FritzTAM(fc=fritz_connection)
    delete_mode = service_call.data["delete_mode"]

    if delete_mode == "specific":
        message_index = service_call.data.get("message_index")
        if message_index is None:
            raise HomeAssistantError(
                "message_index is required when delete_mode is specific"
            )

        await hass.async_add_executor_job(
            lambda: tam.delete_message(messageIndex=message_index)
        )
    else:
        messages = (runtime_data.coordinator.data or {}).get("messages", []) or []
        for message in messages:
            await hass.async_add_executor_job(
                lambda index=int(message["Index"]): tam.delete_message(
                    messageIndex=index
                )
            )

    await runtime_data.coordinator.async_request_refresh()


async def async_setup(
    hass: HomeAssistant,
    config: dict,
) -> bool:
    """Set up integration."""

    hass.http.register_view(MailboxView(hass))

    async def handle_delete_voicemail_message(service_call) -> None:
        await async_delete_voicemail_message(hass, service_call)

    hass.services.async_register(
        DOMAIN,
        SERVICE_DELETE_VOICEMAIL_MESSAGE,
        handle_delete_voicemail_message,
        schema=SERVICE_SCHEMA,
    )

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
    entry: FritzboxVoicemailConfigEntry,
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
    entry: FritzboxVoicemailConfigEntry,
) -> None:
    """Reload integration."""

    await hass.config_entries.async_reload(entry.entry_id)