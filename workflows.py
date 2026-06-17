from temporalio import activity, workflow
from pydantic import BaseModel

from datetime import timedelta
from temporalio.common import RetryPolicy

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

    #raise Exception("Simulated Failure")

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
    ) -> str:

        workflow.logger.info(
            f"Starting workflow for {workflow_input.name}"
            f"request_id={workflow_input.request_id} "
            f"client_id={workflow_input.client_id} "
            f"name={workflow_input.name}"
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
                backoff_coefficient=2.0,
                maximum_interval=timedelta(minutes=1),
                maximum_attempts=5,
            ),
        )

        return {
            "status": "APPROVED",
            "message": result,
        }
        #return result



@workflow.defn
class GoodMorning:

    @workflow.run
    async def run_morning(self, name: str) -> str:
        result = await workflow.execute_activity(
            say_morning,
            name,
            start_to_close_timeout=timedelta(seconds=10),
        )

        return result


from datetime import timedelta