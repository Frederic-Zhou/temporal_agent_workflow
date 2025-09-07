from datetime import timedelta
from temporalio import workflow
from langchain_core.messages import HumanMessage, ToolMessage, AIMessage


@workflow.defn
class AiAgentWorkflow:
    @workflow.run
    async def run(self, query: str) -> str:
        messages = [HumanMessage(query)]
        MAX_STEPS = 8

        for _ in range(MAX_STEPS):
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

        # 返回messages中最后一个 AIMessage 的 content
        last_ai_message = next(
            (msg.content for msg in reversed(messages) if isinstance(msg, AIMessage)),
            None,
        )

        return (
            f"Exceeded maximum steps ({MAX_STEPS}), last AI reply: {last_ai_message}"
            if last_ai_message
            else f"Exceeded maximum steps ({MAX_STEPS}), and no valid AI reply found."
        )
