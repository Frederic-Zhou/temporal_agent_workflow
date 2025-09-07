import asyncio
from temporalio.client import Client
from temporalio.worker import Worker
from workflows import AiAgentWorkflow
from activities import llm_chat, add, division


async def main():
    client = await Client.connect("localhost:7233")
    worker = Worker(
        client,
        task_queue="my-task-queue",
        workflows=[AiAgentWorkflow],
        activities=[llm_chat, add, division],
    )
    print("Worker started.")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
