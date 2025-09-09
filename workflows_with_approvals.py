from datetime import timedelta
from temporalio import workflow
from typing import Optional, Dict
from temporalio.exceptions import ApplicationError


from langchain_core.messages import HumanMessage, ToolMessage, AIMessage


@workflow.defn
class AiAgentWorkflow_WithApprovals:
    def __init__(self):
        # Store approval results: call_id -> "yes"/"no"
        self._approvals: Dict[str, Optional[str]] = {}

    # Approval results are written back by external systems or user interfaces via Signal

    @workflow.signal
    async def approve_tool(self, params: dict):  # "yes" / "no"
        self._approvals[params["call_id"]] = params["decision"]

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

            # End immediately if there are no tool calls
            if not ai_msg.get("tool_calls"):
                return messages[-1].content

            for tc in ai_msg["tool_calls"]:
                name = tc["name"]
                args = tc["args"].get("params", tc["args"])
                call_id = tc.get("id", f"{name}-{workflow.now()}")
                print(f"Workflow got tool call_id: {call_id}")

                # Name starts with uppercase -> requires approval

                if name and name[0].isupper():
                    try:
                        await workflow.wait_condition(
                            lambda: self._approvals.get(call_id) is not None,
                            timeout=timedelta(minutes=30),
                        )
                    except TimeoutError:
                        raise ApplicationError(
                            f"Approval timed out for tool '{name}' (call_id={call_id})",
                            type="ApprovalTimeout",
                            non_retryable=True,
                        )

                    if self._approvals.get(call_id) != "yes":
                        raise ApplicationError(
                            f"Approval denied for tool '{name}' (call_id={call_id})",
                            type="ApprovalDenied",
                            non_retryable=True,
                        )

                # Execute the tool
                result = await workflow.execute_activity(
                    name, args, schedule_to_close_timeout=timedelta(seconds=60)
                )
                messages.append(ToolMessage(content=str(result), tool_call_id=call_id))

        # Exceeded maximum steps without completion
        last_ai = next(
            (m.content for m in reversed(messages) if isinstance(m, AIMessage)), None
        )
        return last_ai or f"Exceeded max steps ({max_steps})."
