from aiohttp import web
from custom_fritzconnection.lib.fritztam import FritzTAM
from homeassistant.components.http import HomeAssistantView

from .const import DOMAIN


class MailboxView(HomeAssistantView):
    url = "/api/mailbox/{message_index}"
    name = "api:mailbox"
    requires_auth = True

    def __init__(self, hass):
        self.hass = hass

    async def get(self, request, message_index):
        runtime_data = next(iter(self.hass.data[DOMAIN].values()))

        tam = FritzTAM(fc=runtime_data.client)

        wav_bytes = await self.hass.async_add_executor_job(
            lambda: tam.message(messageIndex=int(message_index))
        )

        return web.Response(
            body=wav_bytes,
            content_type="audio/wav",
        )
