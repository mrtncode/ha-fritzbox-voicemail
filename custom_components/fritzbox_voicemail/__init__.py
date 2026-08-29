"""Fritzbox Voicemail integration."""

from __future__ import annotations

from typing import TYPE_CHECKING

import voluptuous as vol
from custom_fritzconnection import FritzConnection
from custom_fritzconnection.lib.fritztam import FritzTAM
from homeassistant.const import CONF_PASSWORD, CONF_URL, CONF_USERNAME, Platform
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.loader import async_get_loaded_integration

from .const import CONF_TAM_INDEX, DOMAIN
from .coordinator import FritzboxVoicemailDataUpdateCoordinator
from .data import FritzboxVoicemailConfigEntry, FritzboxVoicemailData
from .views import MailboxView

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant, ServiceCall

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.SWITCH]
CONFIG_SCHEMA = cv.empty_config_schema(DOMAIN)
SERVICE_DELETE_VOICEMAIL_MESSAGE = "delete_voicemail_message"

SERVICE_SCHEMA = vol.All(
    cv.make_entity_service_schema(
        {
            vol.Required("delete_mode"): vol.In(["all", "specific"]),
            vol.Optional("message_index"): cv.positive_int,
        }
    )
)


def _get_target_entries(
    hass: HomeAssistant, entity_ids: list[str]
) -> set[tuple[FritzboxVoicemailConfigEntry, int]]:
    """Sucht die passenden FritzBox Config-Entries und den zugehörigen TAM-Index."""
    target_entries: set[tuple[FritzboxVoicemailConfigEntry, int]] = set()
    ent_reg = er.async_get(hass)

    for entity_id in entity_ids:
        entry = ent_reg.async_get(entity_id)
        if (
            entry
            and entry.config_entry_id
            and (
                config_entry := hass.config_entries.async_get_entry(
                    entry.config_entry_id
                )
            )
            and config_entry.domain == DOMAIN
        ):
            idx = int(config_entry.data.get(CONF_TAM_INDEX, 0))
            target_entries.add((config_entry, idx))

    return target_entries


async def async_delete_message(hass: HomeAssistant, service_call: ServiceCall) -> None:
    """Delete voicemail message(s) from the FritzBox."""
    delete_mode = service_call.data["delete_mode"]
    message_index = service_call.data.get("message_index")

    if delete_mode == "specific" and message_index is None:
        msg = "message_index is required when delete_mode is 'specific'"
        raise HomeAssistantError(msg)

    entity_ids = service_call.data.get("entity_id", [])
    if isinstance(entity_ids, str):
        entity_ids = [entity_ids]

    target_entries = _get_target_entries(hass, entity_ids)

    if not target_entries:
        msg = "No active FritzBox Voicemail integration found."
        raise HomeAssistantError(msg)

    for config_entry, tam_index in target_entries:
        if not (runtime_data := hass.data.get(DOMAIN, {}).get(config_entry.entry_id)):
            continue

        tam = FritzTAM(fc=runtime_data.client)

        if delete_mode == "specific":
            await hass.async_add_executor_job(
                lambda tam=tam, tam_index=tam_index, message_index=message_index: (
                    tam.delete_message(
                        tamIndex=str(tam_index), messageIndex=message_index
                    )
                )
            )
        else:
            messages = (runtime_data.coordinator.data or {}).get("messages", []) or []
            tam_msgs = [
                m for m in messages if str(m.get("Tam", tam_index)) == str(tam_index)
            ]

            def _del_all(
                tam: FritzTAM = tam,
                tam_index: int = tam_index,
                tam_msgs: list = tam_msgs,
            ) -> None:
                for m in tam_msgs:
                    tam.delete_message(
                        tamIndex=str(tam_index), messageIndex=(m["Index"])
                    )

            await hass.async_add_executor_job(_del_all)

        await runtime_data.coordinator.async_request_refresh()


async def async_setup(hass: HomeAssistant, config: dict) -> bool:  # noqa: ARG001
    """Set up the FritzBox Voicemail integration."""
    hass.http.register_view(MailboxView(hass))
    hass.services.async_register(
        DOMAIN,
        SERVICE_DELETE_VOICEMAIL_MESSAGE,
        lambda call: async_delete_message(hass, call),
        schema=SERVICE_SCHEMA,
    )
    return True


async def async_setup_entry(
    hass: HomeAssistant, entry: FritzboxVoicemailConfigEntry
) -> bool:
    """Set up FritzBox Voicemail from a config entry."""
    fritz_connection = await hass.async_add_executor_job(
        lambda: FritzConnection(
            address=entry.data[CONF_URL],
            user=entry.data[CONF_USERNAME],
            password=entry.data[CONF_PASSWORD],
        )
    )

    coordinator = FritzboxVoicemailDataUpdateCoordinator(hass, fritz_connection)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = FritzboxVoicemailData(
        client=fritz_connection,
        coordinator=coordinator,
        integration=async_get_loaded_integration(hass, entry.domain),
    )

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.runtime_data

    # register fritzbox as Hub
    device_reg = dr.async_get(hass)
    device_reg.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, entry.entry_id)},
        name=entry.title or "FRITZ!Box Voicemail",
        manufacturer="AVM",
        model="FRITZ!Box",
    )

    await hass.config_entries.async_forward_entry_setups(
        entry,
        PLATFORMS,
    )

    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

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
