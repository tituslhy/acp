import asyncio

from acp_sdk.client import Client
from acp_sdk.models import (
    Message,
    MessagePart,
)


async def example() -> None:
    async with Client(base_url="http://localhost:8000") as client, client.session() as session:
        run = await session.run_sync(
            agent="echo", inputs=[Message(parts=[MessagePart(content="Howdy!", content_type="text/plain")])]
        )
        run = await session.run_sync(
            agent="echo", inputs=[Message(parts=[MessagePart(content="Howdy again!", content_type="text/plain")])]
        )
        print(run)


if __name__ == "__main__":
    asyncio.run(example())
