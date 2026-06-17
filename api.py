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

WORKFLOW_PERMISSIONS = {
    "HelloWorkflow": ["client-a"],
    "GoodMorningWorkflow": ["client-b"],
}

def validate_workflow_access(
    client_id: str,
    workflow_name: str
):

    allowed_clients = WORKFLOW_PERMISSIONS.get(
        workflow_name,
        []
    )

    if client_id not in allowed_clients:
        raise HTTPException(
            status_code=403,
            detail=(
                f"Client '{client_id}' "
                f"is not allowed to trigger "
                f"'{workflow_name}'"
            )
        )

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
    validate_workflow_access(
        x_client_id,
        "HelloWorkflow"
    )

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
            "run_id": description.run_id,
            "workflow_type": description.workflow_type,
            "status": description.status.name,
            "start_time": description.start_time,
            "close_time": description.close_time,
        }

    except Exception as e:
        return {"message": str(e)}



@app.post("/workflows/morning")
async def trigger_morning(request: HelloRequest,
                          x_client_id: str = Header(...)):

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
                "customer": namespace,
                "workflow_id": workflow_id,
                "run_id": description.run_id,
                "workflow_type": description.workflow_type,
                "status": description.status.name,
                "start_time": description.start_time,
                "close_time": description.close_time,
            }

        except Exception:
            pass

    raise HTTPException(
        status_code=404,
        detail="Workflow not found"
    )


@app.post(
    "/workflows/{workflow_id}/approve"
)
async def approve_workflow(
    workflow_id: str
):

    for namespace, client in (
        app.state.namespace_clients.items()
    ):

        try:

            handle = client.get_workflow_handle(
                workflow_id
            )

            await handle.signal(
                HelloWorkflow.approve
            )

            return {
                "status": "APPROVED",
                "workflow_id": workflow_id,
                "namespace": namespace,
            }

        except Exception:
            pass

    raise HTTPException(
        status_code=404,
        detail="Workflow not found"
    )

@app.post(
    "/workflows/{workflow_id}/reject"
)
async def reject_workflow(
    workflow_id: str
):

    for namespace, client in (
        app.state.namespace_clients.items()
    ):

        try:

            handle = client.get_workflow_handle(
                workflow_id
            )

            await handle.signal(
                HelloWorkflow.reject
            )

            return {
                "status": "REJECTED",
                "workflow_id": workflow_id,
                "namespace": namespace,
            }

        except Exception:
            pass

    raise HTTPException(
        status_code=404,
        detail="Workflow not found"
    )


@app.get(
    "/workflows/{workflow_id}/approval-status"
)
async def approval_status(
    workflow_id: str
):

    for namespace, client in (
        app.state.namespace_clients.items()
    ):

        try:

            handle = client.get_workflow_handle(
                workflow_id
            )

            status = await handle.query(
                HelloWorkflow.get_status
            )

            return {
                "workflow_id": workflow_id,
                "namespace": namespace,
                "approval_state": status,
            }

        except Exception:
            pass

    raise HTTPException(
        status_code=404,
        detail="Workflow not found"
    )