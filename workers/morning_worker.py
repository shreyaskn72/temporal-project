import asyncio

from temporalio.client import Client
from temporalio.worker import Worker

from workflows import GoodMorning, say_morning


async def main():

    client = await Client.connect("localhost:7233")

    worker = Worker(
        client,
        task_queue="morning-task-queue",
        workflows=[GoodMorning],
        activities=[say_morning],
    )

    print("Morning Worker Started")

    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())