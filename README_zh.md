
# Temporal + Langchain ReAct AI Agent 可观测工具调用实现

> 项目地址：[https://github.com/Frederic-Zhou/temporal_agent_workflow](https://github.com/Frederic-Zhou/temporal_agent_workflow)

这篇教程会和你一起，从零搭建一个基于 Temporal 和 Langchain 的可观测 AI Agent 系统。我们会用 ReAct Agent 自动推理、自动调用工具，并且每一步都能在 Temporal 工作流里追踪到。希望你能在动手实践中收获乐趣，也欢迎随时交流你的想法！

---

## 1. 环境准备

1. 启动 Temporal Server（推荐用 docker-compose，几分钟搞定）
2. 安装依赖（项目用 poetry 管理，直接 `poetry install` 即可）
3. 配置好 API KEY（如果你要用外部 LLM，比如 Gemini）

---

## 2. 设计 Agent 工作流

核心逻辑都在 `workflows.py`，我们用 Temporal 工作流来串联 LLM 推理和工具调用：

```python
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
```

---

## 3. 实现工具（Tool）与 LLM 调用

在 `activities.py` 中定义 LLM 及工具逻辑：

```python
@activity.defn
async def llm_chat(messages: list) -> str:
    llm = init_chat_model("gemini-2.0-flash", model_provider="google_genai")
    llm_with_tools = llm.bind_tools([add, division])
    response = llm_with_tools.invoke(messages)
    return response

@activity.defn
async def add(params: list[int]) -> int:
    return sum(params)

class divisionParams(BaseModel):
    a: int = Field(..., description="Numerator")
    b: int = Field(..., description="Denominator, must not be zero", gt=0)

@activity.defn
async def division(params: divisionParams) -> int:
    return params.a // params.b
```

你可以根据自己的需求加更多工具，只要实现 activity 并注册到 worker 就行。

---

## 4. 启动 Worker

`worker.py` 负责注册并运行所有 workflow 和 activity，基本不用怎么改，直接用：

```python
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
```

---

## 5. 启动工作流（提交任务）

用 `starter.py` 提交一个 Agent 推理任务，体验一下完整流程：

```python
async def main():
    client = await Client.connect("localhost:7233")
    result = await client.execute_workflow(
        "AiAgentWorkflow",
        "what is 1 divided by 2 then add 1?",
        id=f"AI-Agent-workflow-{{uuid.uuid4()}}",
        task_queue="my-task-queue",
    )
    print("Workflow result:", result)
```

---

## 6. 可观测性与调试

通过 Temporal UI（默认 http://localhost:8233），你可以实时看到每一次 LLM 推理、工具调用的输入输出、耗时和状态，调试和排查都很方便。

---

## 7. 扩展与进阶

- 想加什么工具都可以，直接写 activity 并注册到 worker。
- 可以集成更多 LLM、外部 API。
- 也可以把这个项目当模板，快速搭建自己的可观测 AI Agent。

---

## 8. 参考与社区

完整代码和更多细节都在：[https://github.com/Frederic-Zhou/temporal_agent_workflow](https://github.com/Frederic-Zhou/temporal_agent_workflow)

如果你有任何问题、想法或者想一起玩，欢迎随时联系我讨论！也可以在 Temporal 社区或 GitHub 提 issue。
