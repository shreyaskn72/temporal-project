import asyncio

from temporalio.client import Client
from temporalio.worker import Worker

from workflows import HelloWorkflow, say_hello, GoodMorning, say_morning
import logging

import os

TEMPORAL_HOST = os.getenv(
    "TEMPORAL_HOST",
    "localhost:7233"
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s"
)

async def main():
    hello_client = await Client.connect(
        TEMPORAL_HOST,
        namespace="customer-a"
    )

    worker = Worker(
        hello_client,
        task_queue="hello-task-queue",
        workflows=[HelloWorkflow],
        activities=[say_hello],
    )

    print("Hello Worker started...")

    await worker.run()

async def main_morning():
    morning_client = await Client.connect(
        TEMPORAL_HOST,
        namespace="customer-b"
    )

    worker = Worker(
        morning_client,
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
