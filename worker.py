import asyncio
from temporalio.client import Client
from temporalio.worker import Worker
from workflows import AiAgentWorkflow
from workflows_with_approvals import AiAgentWorkflow_WithApprovals
from activities import llm_chat, add, Division


async def main():
    client = await Client.connect("localhost:7233")
    worker = Worker(
        client,
        task_queue="my-task-queue",
        workflows=[AiAgentWorkflow, AiAgentWorkflow_WithApprovals],
        activities=[llm_chat, add, Division],
    )
    print("Worker started.")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
