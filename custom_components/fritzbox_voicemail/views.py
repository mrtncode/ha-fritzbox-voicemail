"""Views for audio streaming."""

from typing import TYPE_CHECKING, ClassVar

from aiohttp import web
from custom_fritzconnection.lib.fritztam import FritzTAM
from homeassistant.components.http import HomeAssistantView

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

from .const import DOMAIN


class MailboxView(HomeAssistantView):
    """View to handle requests for voicemail messages from the FritzBox."""

    url = "/api/mailbox/{entry_id}/{tam_index}/{message_index}"
    # Keep the old URLs for backward compatibility
    extra_urls: ClassVar[list[str]] = [
        "/api/mailbox/{tam_index}/{message_index}",
        "/api/mailbox/{message_index}",
    ]
    name = "api:mailbox"
    requires_auth = True

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the mailbox view."""
        self.hass = hass

    async def get(
        self,
        request: web.Request,
        entry_id: str,
        message_index: str,
        tam_index: str | None = None,
    ) -> web.Response:
        """Handle GET requests to retrieve voicemail messages from the FritzBox."""
        if DOMAIN not in self.hass.data or entry_id not in self.hass.data[DOMAIN]:
            return web.Response(status=404)

        if entry_id and entry_id in self.hass.data[DOMAIN]:
            runtime_data = self.hass.data[DOMAIN][entry_id]
        else:
            # Use first entry as fallback
            runtime_data = next(iter(self.hass.data[DOMAIN].values()))

        _request = request
        if not runtime_data:
            return web.Response(status=404)

        if not tam_index:
            return web.Response(status=400)

        if not message_index:
            return web.Response(status=400)

        tam_idx = tam_index if tam_index is not None else "0"
        msg_idx = message_index

        tam = FritzTAM(fc=runtime_data.client)

        try:
            wav_bytes = await self.hass.async_add_executor_job(
                lambda: tam.message(tamIndex=tam_idx, messageIndex=msg_idx)
            )
        except Exception:  # noqa: BLE001
            return web.Response(status=500)

        return web.Response(
            body=wav_bytes,
            content_type="audio/wav",
        )
