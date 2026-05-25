import asyncio

from temporalio.client import Client

from workflows import HelloWorkflow


async def main():
    client = await Client.connect("localhost:7233")

    result = await client.execute_workflow(
        HelloWorkflow.run,
        "Shreyas",
        id="hello-workflow-id",
        task_queue="hello-task-queue",
    )

    print(result)


if __name__ == "__main__":
    asyncio.run(main())