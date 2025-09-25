# agents.py (place in same folder as social_media_agent.py)
from typing import Any, Callable, Dict, List, Optional

class Agent:
    def __init__(self, name: str = "agent"):
        self.name = name
    def act(self, input_data: Any) -> Any:
        return {"status": "ok", "name": self.name, "input": input_data}

class Runner:
    def __init__(self, agent: Agent):
        self.agent = agent
    def run(self, item: Any) -> Any:
        return self.agent.act(item)

# Very minimal WebSearchTool stub
class WebSearchTool:
    def __init__(self):
        pass
    def search(self, q: str) -> List[Dict[str,Any]]:
        return [{"title": "stub result", "snippet": f"search for {q}"}]

# function_tool could be a decorator or factory that registers functions
def function_tool(fn: Callable):
    # simple passthrough decorator
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)
    wrapper._is_function_tool = True
    return wrapper

class ItemHelpers:
    @staticmethod
    def normalize(item: dict) -> dict:
        # placeholder: ensure keys are strings
        return {str(k): v for k, v in (item or {}).items()}

# simple trace utility
def trace(msg: str):
    print("[TRACE]", msg)
