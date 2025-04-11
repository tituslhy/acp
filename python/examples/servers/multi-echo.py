from collections.abc import AsyncGenerator, Generator

from acp_sdk.models import (
    Message,
)
from acp_sdk.server import RunYield, RunYieldResume, Server, SyncContext

# This example showcases several ways to create echo agent using decoratos.

server = Server()


@server.agent(description="Async generator")
async def async_gen_echo(input: Message, context: SyncContext) -> AsyncGenerator[RunYield, RunYieldResume]:
    """Echoes everything"""
    yield {"thought": "I should echo everyting"}
    yield input


@server.agent(description="Async")
async def async_echo(input: Message, context: SyncContext) -> RunYield:
    """Echoes everything"""
    # no mechanism to yield thought, use async gen
    return input


@server.agent(description="Generator")
def gen_echo(input: Message, context: SyncContext) -> Generator[RunYield, RunYieldResume]:
    """Echoes everything"""
    yield {"thought": "I should echo everyting"}
    return input


@server.agent(description="Sync")
def sync_echo(input: Message, context: SyncContext) -> RunYield:
    """Echoes everything"""
    context.yield_({"thought": "I should echo everyting"})
    return input


server.run()
