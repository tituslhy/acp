import asyncio

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse, StreamingResponse

import uvicorn

from acp_sdk.server.agent import Agent
from acp_sdk.models import (
    AgentName,
    Agent as AgentModel,
    AgentsListResponse,
    AgentReadResponse,
    Run,
    RunCancelResponse,
    RunCreateRequest,
    RunCreateResponse,
    RunId,
    RunMode,
    RunReadResponse,
    RunResumeRequest,
    RunResumeResponse,
    RunStatus,
)
from acp_sdk.server.bundle import RunBundle
from acp_sdk.server.utils import stream_sse


def app(*agents: Agent) -> FastAPI:
    app = FastAPI(title="acp-agents")

    agents: dict[AgentName, Agent] = {agent.name: agent for agent in agents}
    runs: dict[RunId, RunBundle] = dict()

    def find_run_bundle(run_id: RunId):
        bundle = runs.get(run_id, None)
        if not bundle:
            raise HTTPException(status_code=404, detail=f"Run {run_id} not found")
        return bundle

    def find_agent(agent_name: AgentName):
        agent = agents.get(agent_name, None)
        if not agent:
            raise HTTPException(status_code=404, detail=f"Agent {agent_name} not found")
        return agent

    @app.get("/agents")
    async def list() -> AgentsListResponse:
        return AgentsListResponse(
            agents=[
                AgentModel(name=agent.name, description=agent.description)
                for agent in agents.values()
            ]
        )

    @app.get("/agents/{name}")
    async def read(name: AgentName) -> AgentReadResponse:
        agent = find_agent(name)
        return AgentModel(name=agent.name, description=agent.description)

    @app.post("/runs")
    async def create(request: RunCreateRequest) -> RunCreateResponse:
        agent = find_agent(request.agent_name)
        bundle = RunBundle(
            agent=agent,
            run=Run(
                agent_name=agent.name,
                session_id=request.session_id,
            ),
        )

        bundle.task = asyncio.create_task(bundle.execute(request.input))
        runs[bundle.run.run_id] = bundle

        match request.mode:
            case RunMode.STREAM:
                return StreamingResponse(
                    stream_sse(bundle),
                    media_type="text/event-stream",
                )
            case RunMode.SYNC:
                await bundle.join()
                return bundle.run
            case RunMode.ASYNC:
                return JSONResponse(
                    status_code=status.HTTP_202_ACCEPTED,
                    content=bundle.run.model_dump(),
                )
            case _:
                raise NotImplementedError()

    @app.get("/runs/{run_id}")
    async def read(run_id: RunId) -> RunReadResponse:
        bundle = find_run_bundle(run_id)
        return bundle.run

    @app.post("/runs/{run_id}")
    async def resume(run_id: RunId, request: RunResumeRequest) -> RunResumeResponse:
        bundle = find_run_bundle(run_id)
        bundle.stream_queue = asyncio.Queue()  # TODO improve
        await bundle.await_queue.put(request.await_)
        match request.mode:
            case RunMode.STREAM:
                return StreamingResponse(
                    stream_sse(bundle),
                    media_type="text/event-stream",
                )
            case RunMode.SYNC:
                await bundle.join()
                return bundle.run
            case RunMode.ASYNC:
                return JSONResponse(
                    status_code=status.HTTP_202_ACCEPTED,
                    content=bundle.run.model_dump(),
                )
            case _:
                raise NotImplementedError()

    @app.post("/runs/{run_id}/cancel")
    async def cancel(run_id: RunId) -> RunCancelResponse:
        bundle = find_run_bundle(run_id)
        if bundle.run.status.is_terminal:
            raise HTTPException(
                status_code=403,
                detail=f"Run with terminal status {bundle.run.status} can't be cancelled",
            )
        bundle.task.cancel()
        bundle.run.status = RunStatus.CANCELLING
        return JSONResponse(
            status_code=status.HTTP_202_ACCEPTED, content=bundle.run.model_dump()
        )

    return app


async def serve(*agents: Agent, **kwargs):
    config = uvicorn.Config(app=app(*agents), **kwargs)
    server = uvicorn.Server(config)
    await server.serve()
