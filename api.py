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


NAMESPACES = [
    "customer-a",
    "customer-b",
]

@app.on_event("startup")
async def startup():

    app.state.namespace_clients = {}

    for namespace in NAMESPACES:
        app.state.namespace_clients[namespace] = (
            await Client.connect(
                "localhost:7233",
                namespace=namespace
            )
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

    handle = await app.state.namespace_clients["customer-a"].start_workflow(
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

    if customer not in NAMESPACES:
        return {"message": "customer not found"}

    handle = app.state.namespace_clients[customer].get_workflow_handle(workflow_id)

    try:
        description = await handle.describe()

        return {
            "customer": customer,
            "workflow_id": workflow_id,
            "status": description.status.name,
        }

    except Exception as e:
        return {"message": str(e)}



@app.post("/workflows/morning")
async def trigger_morning(request: HelloRequest):

    workflow_id = f"morning-{uuid.uuid4()}"

    handle = await app.state.namespace_clients["customer-b"].start_workflow(
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

# universal status api for all namespaces
@app.get("/workflows/status/{workflow_id}")
async def get_workflow_status(workflow_id: str):

    for namespace, client in app.state.namespace_clients.items():

        try:
            handle = client.get_workflow_handle(workflow_id)

            description = await handle.describe()

            return {
                "namespace": namespace,
                "workflow_id": workflow_id,
                "status": description.status.name,
            }

        except Exception:
            pass

    raise HTTPException(
        status_code=404,
        detail="Workflow not found"
    )