import asyncio

from temporalio.client import Client

from workflows import HelloWorkflow, GoodMorning


async def main():
    client = await Client.connect("localhost:7233")

    result = await client.execute_workflow(
        HelloWorkflow.run,
        "Shreyas",
        id="hello-workflow-id",
        task_queue="hello-task-queue",
    )

    print(result)

async def morning():
    client = await Client.connect("localhost:7233")

    result = await client.execute_workflow(
        GoodMorning.run_morning,
        "Shreyas",
        id="morning-workflow-id",
        task_queue="morning-task-queue",
    )

    print(result)


if __name__ == "__main__":
    asyncio.run(main())
    asyncio.run(morning())