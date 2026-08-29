"""Media source for Fritzbox Voicemail."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components import media_source
from homeassistant.components.media_player.const import MediaClass

from .const import DOMAIN

if TYPE_CHECKING:
    from homeassistant.components.media_source.models import MediaSourceItem
    from homeassistant.core import HomeAssistant


async def async_get_media_source(hass: HomeAssistant) -> media_source.MediaSource:
    """Set up media source."""
    return MailboxMediaSource(DOMAIN, hass)


class MailboxMediaSource(media_source.MediaSource):
    """Media source for Fritzbox Voicemail."""

    def __init__(self, domain: str, hass: HomeAssistant) -> None:
        """Initialize the media source."""
        super().__init__(domain)
        self.hass = hass
        self.name = "Mailbox"

    async def async_browse_media(
        self,
        item: MediaSourceItem,  # noqa: ARG002
    ) -> media_source.BrowseMediaSource:
        """Browse media items."""
        entries = self.hass.data.get(DOMAIN, {})
        children = []

        # Run for every fritzbox
        for entry_id, runtime_data in entries.items():
            messages = (
                runtime_data.coordinator.data.get("messages", [])
                if runtime_data.coordinator.data
                else []
            )

            for msg in messages:
                tam_idx = msg.get("Tam", 0)

                title = str(msg["Number"]) if msg.get("Number") else "Unknown"
                if msg.get("Name"):
                    title += " - " + msg["Name"]
                if msg.get("Date"):
                    title += " - " + msg["Date"]

                children.append(
                    media_source.BrowseMediaSource(
                        domain=DOMAIN,
                        identifier=f"{entry_id}/{tam_idx}/{msg['Index']}",
                        media_class=MediaClass.MUSIC,
                        media_content_type="audio/wav",
                        title=title,
                        can_play=True,
                        can_expand=False,
                    )
                )

        return media_source.BrowseMediaSource(
            domain=DOMAIN,
            identifier=None,
            media_class=MediaClass.APP,
            media_content_type="",
            title="Mailbox",
            can_play=False,
            can_expand=True,
            children=children,
        )

    async def async_resolve_media(
        self, item: MediaSourceItem
    ) -> media_source.PlayMedia:
        """Resolve media item to a playable URL."""
        parts = item.identifier.split("/")
        min_parts = 3
        if len(parts) < min_parts:
            e = "Invalid media identifier"
            raise media_source.Unresolvable(e)

        entry_id, tam_idx, msg_idx = parts[0], parts[1], parts[2]

        if DOMAIN not in self.hass.data or entry_id not in self.hass.data[DOMAIN]:
            e = f"FritzBox entry {entry_id} not found"
            raise media_source.Unresolvable(e)

        return media_source.PlayMedia(
            url=f"/api/mailbox/{entry_id}/{tam_idx}/{msg_idx}",
            mime_type="audio/wav",
        )
