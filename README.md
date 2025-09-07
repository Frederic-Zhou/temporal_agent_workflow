# Temporal + Langchain AI Agent 项目说明

本项目结合了 [Temporal](https://temporal.io/) 工作流引擎与 [Langchain](https://python.langchain.com/) 框架，构建了一个具备可观测性的 AI Agent 系统。该系统实现了 ReAct Agent，能够自动调用多种工具（Tools），并返回最终结果。通过 Temporal，可以详细追踪每一次 LLM 调用及工具调用的全过程。

## 项目亮点

- **ReAct Agent 实现**：基于 Langchain，支持自动推理与工具调用。
- **Temporal 工作流集成**：所有 Agent 推理与工具调用过程均通过 Temporal 工作流编排，具备高可观测性。
- **可扩展的工具体系**：支持自定义和扩展工具，满足多样化需求。
- **详细的调用追踪**：每一次 LLM 及工具调用都可在 Temporal UI 中可视化追踪。

## 主要文件结构

- `workflows.py`：定义了 Temporal 工作流，负责 orchestrate Agent 推理与工具调用。
- `activities.py`：实现了具体的工具（Tool）逻辑，供 Agent 调用。
- `worker.py`：启动 Temporal Worker，监听并执行工作流与活动。
- `starter.py`：工作流启动入口，负责提交任务到 Temporal。

## 关键代码片段


### 1. 工作流定义（`workflows.py`）

```python
# ...existing code...
@workflow.defn
class AgentWorkflow:
    @workflow.run
    async def run(self, input):
        # 这里 orchestrate LLM 推理与工具调用
        # ...existing code...
```


### 2. 工具实现（`activities.py`）

```python
# ...existing code...
@activity.defn
async def search_tool(query: str) -> str:
    # 具体工具逻辑实现
    # ...existing code...
```


### 3. Worker 启动（`worker.py`）

```python
# ...existing code...
async def main():
    # 启动 Temporal Worker，注册工作流与活动
    # ...existing code...
```


### 4. 启动工作流（`starter.py`）

```python
# ...existing code...
async def main():
    # 提交 AgentWorkflow 到 Temporal
    # ...existing code...
```

## 可观测性与调试

通过 Temporal UI，可以实时查看每一次 LLM 推理、工具调用的输入输出、耗时与状态，极大提升了 AI Agent 系统的可观测性与可维护性。


## 适用场景

- 需要高可靠性、可观测性的 AI Agent 系统
- 需要自动化工具调用与复杂推理流程的场景
- 需要对 LLM 推理与外部调用过程进行详细追踪的应用

---

如需进一步了解或贡献，欢迎访问 Temporal 官方社区或联系项目作者。
