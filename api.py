# app.py

import uuid

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

from temporalio.client import Client
from temporalio.service import RPCError

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
async def trigger_hello_workflow(
    request: HelloRequest,
    x_client_id: str = Header(...)
):
    """
    Start HelloWorkflow
    """

    workflow_id = f"hello-{uuid.uuid4()}"

    print(
        f"Workflow requested "
        f"client={x_client_id} "
        f"workflow_id={workflow_id} "
        f"name={request.name}"
    )

    handle = await app.state.temporal_client.start_workflow(
        HelloWorkflow.run,
        request.name,
        id=workflow_id,
        task_queue="hello-task-queue",
    )

    return {
        "status": "STARTED",
        "workflow_id": handle.id,
        "run_id": handle.result_run_id,
        "client_id": x_client_id,
    }


@app.get("/workflows/{workflow_id}")
async def get_workflow_status(workflow_id: str):

    client = app.state.temporal_client

    try:

        handle = client.get_workflow_handle(workflow_id)

        description = await handle.describe()

        return {
            "workflow_id": workflow_id,
            "run_id": description.run_id,
            "workflow_type": description.workflow_type,
            "status": description.status.name,
            "start_time": description.start_time,
            "close_time": description.close_time,
        }

    except RPCError:
        raise HTTPException(
            status_code=404,
            detail=f"Workflow '{workflow_id}' not found"
        )


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