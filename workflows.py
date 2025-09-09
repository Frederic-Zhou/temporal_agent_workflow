from datetime import timedelta
from temporalio import workflow
from langchain_core.messages import HumanMessage, ToolMessage, AIMessage


@workflow.defn
class AiAgentWorkflow:
    @workflow.run
    async def run(self, query: str, max_steps: int = 8) -> str:
        messages = [HumanMessage(query)]

        for _ in range(max_steps):
            ai_msg = await workflow.execute_activity(
                "llm_chat",
                messages,
                schedule_to_close_timeout=timedelta(seconds=60),
            )

            messages.append(AIMessage(**ai_msg))

            if ai_msg["tool_calls"]:
                for tool_call in ai_msg["tool_calls"]:
                    print(f"Workflow got tool call: {tool_call}")

                    tool_call_result = await workflow.execute_activity(
                        tool_call["name"],
                        tool_call["args"]["params"],
                        schedule_to_close_timeout=timedelta(seconds=10),
                    )

                    messages.append(
                        ToolMessage(
                            content=str(tool_call_result),
                            tool_call_id=tool_call["id"],
                        )
                    )
            else:
                return messages[-1].content

        # Return the content of the last AIMessage in messages
        last_ai_message = next(
            (msg.content for msg in reversed(messages) if isinstance(msg, AIMessage)),
            None,
        )

        return (
            f"Exceeded maximum steps ({max_steps}), last AI reply: {last_ai_message}"
            if last_ai_message
            else f"Exceeded maximum steps ({max_steps}), and no valid AI reply found."
        )
