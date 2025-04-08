from collections.abc import AsyncGenerator

from pydantic import BaseModel

from acp_sdk.server.bundle import RunBundle


def encode_sse(model: BaseModel) -> str:
    return f"data: {model.model_dump_json()}\n\n"


async def stream_sse(bundle: RunBundle) -> AsyncGenerator[str]:
    async for event in bundle.stream():
        yield encode_sse(event)
