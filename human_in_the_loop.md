Yes. For your current project, I would implement the complete flow like this:

```text
POST /workflows/hello
           │
           ▼
HelloWorkflow
           │
           ▼
WAITING_FOR_APPROVAL
           │
     ┌─────┴─────┐
     ▼           ▼
 APPROVE      REJECT
     │           │
     ▼           ▼
 say_hello    END
     │
     ▼
 COMPLETE
```

and add:

```text
✓ Approve API
✓ Reject API
✓ Query current state
✓ Approval timeout (24h)
✓ Status API integration
```

---

# 1. workflows.py

Replace your current `HelloWorkflow` with:

```python
from temporalio import workflow, activity
from temporalio.common import RetryPolicy

from pydantic import BaseModel

from datetime import timedelta


class HelloWorkflowInput(BaseModel):
    name: str
    client_id: str
    request_id: str


@activity.defn
async def say_hello(name: str) -> str:

    info = activity.info()

    activity.logger.info(
        f"Attempt={info.attempt} "
        f"Executing say_hello for {name}"
    )

    return f"Hello {name} from Temporal!"


@activity.defn
async def say_morning(name: str) -> str:
    return f"Good morning {name} sir!"


@workflow.defn
class HelloWorkflow:

    def __init__(self):

        self.decision = None

    @workflow.signal
    async def approve(self):

        self.decision = "APPROVED"

    @workflow.signal
    async def reject(self):

        self.decision = "REJECTED"

    @workflow.query
    def get_status(self):

        if self.decision is None:
            return "WAITING_FOR_APPROVAL"

        return self.decision

    @workflow.run
    async def run(
        self,
        workflow_input: HelloWorkflowInput,
    ):

        workflow.logger.info(
            f"Workflow started "
            f"request_id={workflow_input.request_id}"
        )

        try:

            await workflow.wait_condition(
                lambda: self.decision is not None,
                timeout=timedelta(hours=24),
            )

        except TimeoutError:

            self.decision = "TIMEOUT"

            return {
                "status": "TIMEOUT",
                "message": "Approval not received"
            }

        if self.decision == "REJECTED":

            return {
                "status": "REJECTED",
                "message": "Rejected by approver"
            }

        result = await workflow.execute_activity(
            say_hello,
            workflow_input.name,
            start_to_close_timeout=timedelta(seconds=10),
            retry_policy=RetryPolicy(
                initial_interval=timedelta(seconds=5),
                backoff_coefficient=2,
                maximum_interval=timedelta(minutes=1),
                maximum_attempts=5,
            ),
        )

        return {
            "status": "APPROVED",
            "message": result,
        }


@workflow.defn
class GoodMorning:

    @workflow.run
    async def run_morning(self, name: str):

        return await workflow.execute_activity(
            say_morning,
            name,
            start_to_close_timeout=timedelta(seconds=10),
        )
```

---

# 2. Add Approve API

In `api.py`

```python
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
```

---

# 3. Add Reject API

```python
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
```

---

# 4. Add Query API

```python
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
```

---

# 5. Example Run

Start workflow:

```bash
curl -X POST \
http://localhost:8000/workflows/hello \
-H "X-Client-Id: client-a" \
-H "Content-Type: application/json" \
-d '{"name":"Shreyas"}'
```

Response:

```json
{
  "status": "STARTED",
  "workflow_id": "hello-123"
}
```

---

Check approval state:

```bash
GET /workflows/hello-123/approval-status
```

Response:

```json
{
  "approval_state": "WAITING_FOR_APPROVAL"
}
```

---

Approve:

```bash
POST /workflows/hello-123/approve
```

Response:

```json
{
  "status": "APPROVED"
}
```

Workflow resumes immediately.

---

Or Reject:

```bash
POST /workflows/hello-123/reject
```

Response:

```json
{
  "status": "REJECTED"
}
```

Workflow ends without running `say_hello`.

---

# 6. Update Existing Status API (Recommended)

Enhance your current status endpoint by including approval state:

```python
approval_state = await handle.query(
    HelloWorkflow.get_status
)
```

and return:

```python
{
    "workflow_id": workflow_id,
    "workflow_status": description.status.name,
    "approval_state": approval_state,
}
```

Now you'll see:

```json
{
  "workflow_status": "RUNNING",
  "approval_state": "WAITING_FOR_APPROVAL"
}
```

which is much more informative.

---

This implementation teaches almost all core Temporal concepts:

* Signals (`approve`, `reject`)
* Queries (`get_status`)
* Long-running workflows
* Human approval
* Workflow state management
* Activity retries
* Timeout handling
* API-driven workflow orchestration

It's a very realistic foundation for the GitHub deployment approval workflows.
