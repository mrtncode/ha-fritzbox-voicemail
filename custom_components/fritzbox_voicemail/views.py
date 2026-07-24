from typing import TYPE_CHECKING

from aiohttp import web
from custom_fritzconnection.lib.fritztam import FritzTAM
from homeassistant.components.http import HomeAssistantView

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

from .const import DOMAIN


class MailboxView(HomeAssistantView):
    """View to handle requests for voicemail messages from the FritzBox."""

    url = "/api/mailbox/{message_index}"
    name = "api:mailbox"
    requires_auth = True

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the mailbox view."""
        self.hass = hass

    async def get(self, request: web.Request, message_index: str) -> web.Response:
        """Handle GET requests to retrieve voicemail messages from the FritzBox."""
        runtime_data = next(iter(self.hass.data[DOMAIN].values()))
        _request = request

        tam = FritzTAM(fc=runtime_data.client)

        wav_bytes = await self.hass.async_add_executor_job(
            lambda: tam.message(messageIndex=int(message_index))
        )

        return web.Response(
            body=wav_bytes,
            content_type="audio/wav",
        )
