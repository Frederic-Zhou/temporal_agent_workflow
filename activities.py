from temporalio import activity
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
from pydantic import BaseModel, Field


@activity.defn
async def llm_chat(messages: list) -> str:

    load_dotenv()

    llm = init_chat_model("gemini-2.0-flash", model_provider="google_genai")
    llm_with_tools = llm.bind_tools([add, Division])

    response = llm_with_tools.invoke(messages)

    return response


@activity.defn
async def add(params: list[int]) -> int:
    """Add two integers.

    Args:
        params: List of integers to add, e.g. [1, 2, 3]
    """
    return sum(params)


class divisionParams(BaseModel):
    """Divide two integers."""

    a: int = Field(..., description="Numerator")
    b: int = Field(..., description="Denominator, must not be zero", gt=0)


@activity.defn
async def Division(params: divisionParams) -> int:
    """Divide two integers.

    Args:
        params: divisionParams of integers to divide, e.g. {"a": 1, "b": 2}
    """
    return params.a / params.b
