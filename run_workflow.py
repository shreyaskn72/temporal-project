import asyncio
import uuid

from temporalio.client import Client

from workflows import HelloWorkflow, GoodMorning, HelloWorkflowInput


async def run_hello():

    client = await Client.connect(
        "localhost:7233",
        namespace="customer-a"
    )

    return await client.execute_workflow(
        HelloWorkflow.run,
        HelloWorkflowInput(
            name="Shreyas",
            client_id="client-123",  # Add required fields
            request_id="request-456"
        ),
        id=f"hello-{uuid.uuid4()}",
        task_queue="hello-task-queue",
    )


async def run_morning():

    client = await Client.connect(
        "localhost:7233",
        namespace="customer-b"
    )

    return await client.execute_workflow(
        GoodMorning.run_morning,
        "Shreyas",
        id=f"morning-{uuid.uuid4()}",
        task_queue="morning-task-queue",
    )


async def main():

    hello_result, morning_result = await asyncio.gather(
        run_hello(),
        run_morning(),
    )

    print("Hello:", hello_result)
    print("Morning:", morning_result)


if __name__ == "__main__":
    asyncio.run(main())