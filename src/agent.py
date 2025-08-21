from typing import List, Dict, Callable, Any
import anthropic
import openai
import os

class Agent:
    """LLM agent with tools for code editing."""

    def __init__(self, model: str = "claude-3-5-sonnet-20240620"):
        self.model = model
        self.client = self._create_client()
        self.tools: Dict[str, Callable] = {}  # load tools here if needed

    def _create_client(self) -> Any:
        """Create LLM client based on model."""
        if "claude" in self.model:
            return anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        elif "gpt" in self.model or "o1" in self.model:
            return openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        raise ValueError(f"Unsupported model: {self.model}")

    def add_tool(self, name: str, func: Callable):
        """Add a tool to the agent."""
        self.tools[name] = func

    def chat(self, prompt: str, history: List[Dict[str, str]] = None) -> str:
        """Chat with LLM, handling tools if needed."""
        messages = history or []
        messages.append({"role": "user", "content": prompt})
        create_kwargs = {
            "model": self.model,
            "messages": messages,
            "max_tokens": 4096,
        }
        if self.tools:
            create_kwargs["tools"] = [{"name": t, "input_schema": {}} for t in self.tools]
        response = self.client.messages.create(**create_kwargs)

        # handle tool calls if present (simplified)
        if hasattr(response, "tool_calls"):
            for tool_call in response.tool_calls:
                tool_name = tool_call.function.name
                if tool_name in self.tools:
                    tool_result = self.tools[tool_name](**tool_call.function.arguments)
                    messages.append({"role": "assistant", "content": str(tool_result)})
                    return self.chat("", messages)
                
        return response.content[0].text if "claude" in self.model else response.choices[0].message.content