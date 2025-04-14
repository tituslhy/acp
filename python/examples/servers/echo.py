import asyncio
from collections.abc import AsyncGenerator

from acp_sdk.models import (
    Message,
)
from acp_sdk.server import Context, RunYield, RunYieldResume, Server

server = Server()


@server.agent()
async def echo(input: Message, context: Context) -> AsyncGenerator[RunYield, RunYieldResume]:
    """Echoes everything"""
    for part in input:
        await asyncio.sleep(0.5)
        yield {"thought": "I should echo everyting"}
        await asyncio.sleep(0.5)
        yield Message(part)


server()
