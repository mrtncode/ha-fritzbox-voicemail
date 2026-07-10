from __future__ import annotations

from io import BytesIO

from homeassistant.components import media_source
from homeassistant.components.media_player.const import MediaClass
from homeassistant.core import HomeAssistant
from .const import DOMAIN
from custom_fritzconnection.lib.fritztam import FritzTAM


async def async_get_media_source(hass: HomeAssistant):
    return MailboxMediaSource(DOMAIN, hass)


class MailboxMediaSource(media_source.MediaSource):
    def __init__(self, domain: str, hass: HomeAssistant):
        super().__init__(domain)
        self.hass = hass
        runtime_data = next(iter(self.hass.data[DOMAIN].values()))
        self.fritz_connection = runtime_data.client
        self.name = "Mailbox"

    async def async_browse_media(self, item):
        tam = FritzTAM(fc=self.fritz_connection)
        messages = await self.hass.async_add_executor_job(tam.message_list) # use default TAM with index 0
        children = [
            media_source.BrowseMediaSource(
                domain=DOMAIN,
                identifier=str(msg["Index"]),
                media_class=MediaClass.MUSIC,
                media_content_type="audio/wav",
                title=msg["Number"] + " - " + msg["Date"] + (" - " + msg["Name"] if msg.get("Name") else ""), # include msg["Name"] if available
                can_play=True,
                can_expand=False,
            )
            for msg in messages
        ]

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

    async def async_resolve_media(self, item):
        return media_source.PlayMedia(
            url=f"/api/mailbox/{item.identifier}",
            mime_type="audio/wav",
        )