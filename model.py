from typing import Optional
import hikari
import aiohttp


class Model:
    def __init__(self) -> None:
        self._client_session: Optional[aiohttp.ClientSession] = None

    @property
    def client_session(self) -> aiohttp.ClientSession:
        assert self._client_session
        return self._client_session

    async def on_starting(self, _: hikari.StartingEvent) -> None:
        self._client_session = aiohttp.ClientSession()

    async def on_stopping(self, _: hikari.StoppingEvent) -> None:
        await self.client_session.close()
