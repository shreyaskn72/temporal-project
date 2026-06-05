from temporalio import activity, workflow
from pydantic import BaseModel

from datetime import timedelta


class HelloWorkflowInput(BaseModel):
    name: str
    client_id: str
    request_id: str

@activity.defn
async def say_hello(name: str) -> str:
    return f"Hello {name} from Temporal!"

@activity.defn
async def say_morning(name: str) -> str:
    return f"Good morning {name} sir!"


@workflow.defn
class HelloWorkflow:

    @workflow.run
    async def run(
        self,
        workflow_input: HelloWorkflowInput,
    ) -> str:

        workflow.logger.info(
            f"request_id={workflow_input.request_id} "
            f"client_id={workflow_input.client_id} "
            f"name={workflow_input.name}"
        )

        result = await workflow.execute_activity(
            say_hello,
            workflow_input.name,
            start_to_close_timeout=timedelta(seconds=10),
        )

        return result


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