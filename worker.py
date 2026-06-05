import asyncio

from temporalio.client import Client
from temporalio.worker import Worker

from workflows import HelloWorkflow, say_hello, GoodMorning, say_morning


async def main():
    client = await Client.connect("localhost:7233")

    worker = Worker(
        client,
        task_queue="hello-task-queue",
        workflows=[HelloWorkflow],
        activities=[say_hello],
    )

    print("Hello Worker started...")

    await worker.run()

async def main_morning():
    client = await Client.connect("localhost:7233")

    worker = Worker(
        client,
        task_queue="morning-task-queue",
        workflows=[GoodMorning],
        activities=[say_morning],
    )

    print("Morning Worker started...")

    await worker.run()

async def run_workers():
    async with asyncio.TaskGroup() as tg:
        tg.create_task(main())
        tg.create_task(main_morning())

if __name__ == "__main__":
    #asyncio.run(main())
    asyncio.run(run_workers())
