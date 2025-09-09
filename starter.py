import asyncio
import uuid
from temporalio.client import Client


async def main():
    client = await Client.connect("localhost:7233")
    result = await client.execute_workflow(
        "AiAgentWorkflow_WithApprovals",
        "what is 1 divided by 2 then add 1?",
        id=f"AI-Agent-workflow-{uuid.uuid4()}",
        task_queue="my-task-queue",
    )
    print("Workflow result:", result)


if __name__ == "__main__":
    asyncio.run(main())
