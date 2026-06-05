# app.py

import uuid

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

from temporalio.client import Client
from temporalio.service import RPCError

from workflows import HelloWorkflow, GoodMorning,  HelloWorkflowInput

app = FastAPI()

import logging

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

class HelloRequest(BaseModel):
    name: str


@app.on_event("startup")
async def startup():
    app.state.customer_a_client = await Client.connect(
        "localhost:7233",
        namespace="customer-a"
    )

    app.state.customer_b_client = await Client.connect(
        "localhost:7233",
        namespace="customer-b"
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

    request_id = str(uuid.uuid4())

    workflow_input = HelloWorkflowInput(
        name=request.name,
        client_id=x_client_id,
        request_id=request_id,
    )

    # AUDIT LOG
    logger.info(
        {
            "event": "workflow_start_requested",
            "workflow_type": "HelloWorkflow",
            "workflow_id": workflow_id,
            "request_id": request_id,
            "client_id": x_client_id,
            "name": request.name,
        }
    )

    handle = await app.state.customer_a_client.start_workflow(
        HelloWorkflow.run,
        workflow_input,
        id=workflow_id,
        task_queue="hello-task-queue",
    )

    return {
        "status": "STARTED",
        "workflow_id": handle.id,
        "run_id": handle.result_run_id,
        "request_id": request_id,
        "client_id": x_client_id,
    }


@app.get("/workflows/status/{customer}/{workflow_id}")
async def get_status(customer: str, workflow_id: str):

    if customer == "customer-a":
        client = app.state.customer_a_client
    elif customer == "customer-b":
        client = app.state.customer_b_client
    else:
        raise HTTPException(400, "Unknown customer")

    handle = client.get_workflow_handle(workflow_id)

    description = await handle.describe()

    return {
        "customer": customer,
        "workflow_id": workflow_id,
        "status": description.status.name,
    }


@app.post("/workflows/morning")
async def trigger_morning(request: HelloRequest):

    workflow_id = f"morning-{uuid.uuid4()}"

    handle = await app.state.customer_b_client.start_workflow(
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