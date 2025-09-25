# agents/runner.py
from typing import Any

class Runner:
    """
    Minimal Runner stub that runs Agent.run(...) and returns its value.
    """
    def __init__(self, agent=None):
        self.agent = agent

    def run(self, *args, **kwargs) -> Any:
        if self.agent is None:
            raise RuntimeError("Runner has no agent set")
        if not hasattr(self.agent, "run"):
            raise RuntimeError("Agent does not implement run()")
        return self.agent.run(*args, **kwargs)

class WebSearchTool:
    """
    Very small websearch stub. Replace with a real websearch integration.
    """
    def __init__(self, provider: str = "stub"):
        self.provider = provider

    def search(self, query: str, limit: int = 5):
        # Replace this implementation with calls to an actual search API.
        return [{"title": f"Result for {query}", "url": "https://example.com", "snippet": "This is a stub."}]
