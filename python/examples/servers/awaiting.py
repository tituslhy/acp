from typing import AsyncGenerator

from acp_sdk.models import (
    Message,
    Await,
    AwaitResume,
    TextMessagePart,
)
from acp_sdk.server import Agent

from acp_sdk.server.context import Context
from acp_sdk.server.server import create_app


class AwaitingAgent(Agent):
    @property
    def name(self):
        return "awaiting"

    @property
    def description(self):
        return "Greets and awaits for more data"

    async def run(
        self, input: Message, *, context: Context
    ) -> AsyncGenerator[Message | Await, AwaitResume]:
        yield Message(TextMessagePart(content="Hello!"))
        data = yield Await()
        yield Message(TextMessagePart(content=f"Thanks for {data}"))


app = create_app(AwaitingAgent())
