from functools import lru_cache

from langchain.agents import create_agent
from langchain.agents.middleware import (
    ModelCallLimitMiddleware,
    ToolCallLimitMiddleware,
)
from langchain.agents.structured_output import ToolStrategy

from app.core.settings import settings
from app.core.llm import get_chat_model
from app.schemas.agent import ModelAnswer
from app.tools import TOOLS
from app.prompts import load_prompt


@lru_cache(maxsize=1)
def get_agent():
    """Structured output(ModelAnswer)을 반환하는 agent 싱글톤."""
    return create_agent(
        model=get_chat_model(),
        tools=TOOLS,
        system_prompt=load_prompt("agent_system"),
        response_format=ToolStrategy(ModelAnswer),
        middleware=[
            ModelCallLimitMiddleware(run_limit=int(settings.MAX_MODEL_CALLS)),
            ToolCallLimitMiddleware(run_limit=int(settings.MAX_TOOL_CALLS)),
        ],
    )