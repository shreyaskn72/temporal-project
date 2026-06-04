# app.py

import uuid

from fastapi import FastAPI
from pydantic import BaseModel

from temporalio.client import Client

from workflows import HelloWorkflow, GoodMorning

app = FastAPI()


class HelloRequest(BaseModel):
    name: str


@app.on_event("startup")
async def startup():
    app.state.temporal_client = await Client.connect(
        "localhost:7233"
    )


@app.post("/workflows/hello")
async def trigger_hello_workflow(request: HelloRequest):

    workflow_id = f"hello-{uuid.uuid4()}"

    handle = await app.state.temporal_client.start_workflow(
        HelloWorkflow.run,
        request.name,
        id=workflow_id,
        task_queue="hello-task-queue",
    )

    return {
        "message": "Workflow started",
        "workflow_id": handle.id,
        "run_id": handle.result_run_id,
    }


@app.post("/workflows/morning")
async def trigger_morning(request: HelloRequest):

    workflow_id = f"morning-{uuid.uuid4()}"

    handle = await app.state.temporal_client.start_workflow(
        GoodMorning.run_morning,
        request.name,
        id=workflow_id,
        task_queue="morning-task-queue",
    )

    return {
        "message": "Workflow started",
        "workflow_id": handle.id,
        "run_id": handle.result_run_id,
    }