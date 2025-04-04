from acp_sdk.models import (
    Message,
)
from acp_sdk.server import Agent, create_app

from acp_sdk.server.context import Context


class EchoAgent(Agent):
    @property
    def name(self):
        return "echo"

    @property
    def description(self):
        return "Echoes everything"

    async def run(self, input: Message, *, context: Context):
        yield input


app = create_app(EchoAgent())
