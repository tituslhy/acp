from collections.abc import AsyncGenerator
from typing import Any

from acp_sdk.models import (
    AwaitRequest,
    AwaitResume,
    Message,
    MessagePart,
)
from acp_sdk.server import Context, Server

server = Server()


@server.agent()
async def awaiting(
    inputs: list[Message], context: Context
) -> AsyncGenerator[Message | AwaitRequest | Any, AwaitResume]:
    """Greets and awaits for more data"""
    yield MessagePart(content="Hello!", content_type="text/plain")
    data = yield AwaitRequest()
    yield MessagePart(content=f"Thanks for {data}", content_type="text/plain")


server.run()
