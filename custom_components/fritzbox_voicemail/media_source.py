"""Media source for Fritzbox Voicemail."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components import media_source
from homeassistant.components.media_player.const import MediaClass

from .const import DOMAIN

if TYPE_CHECKING:
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
        item: media_source.MediaSourceItem,  # noqa: ARG002
    ) -> media_source.BrowseMediaSource:
        """Browse media items."""
        runtime_data = next(iter(self.hass.data[DOMAIN].values()))
        messages = (
            runtime_data.coordinator.data.get("messages", [])
            if runtime_data.coordinator.data
            else []
        )

        children = []
        for msg in messages:
            tam_idx = msg.get("Tam")
            if tam_idx is None:
                tam_idx = 0

            children.append(
                media_source.BrowseMediaSource(
                    domain=DOMAIN,
                    identifier=f"{tam_idx}/{msg['Index']}",
                    media_class=MediaClass.MUSIC,
                    media_content_type="audio/wav",
                    title=msg["Number"]
                    + " - "
                    + msg["Date"]
                    + (" - " + msg["Name"] if msg.get("Name") else ""),
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
        self, item: media_source.MediaSourceItem
    ) -> media_source.PlayMedia:
        """Resolve media item to a playable URL."""
        return media_source.PlayMedia(
            url=f"/api/mailbox/{item.identifier}",
            mime_type="audio/wav",
        )
