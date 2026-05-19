import unittest
import sys
from types import SimpleNamespace
from unittest.mock import Mock, patch


groq_stub = SimpleNamespace(Groq=Mock())

with patch.dict(sys.modules, {"groq": groq_stub}):
    from core.engine import JarvisEngine


class FakeFunction:
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments


class FakeToolCall:
    def __init__(self, name, arguments, call_id="call_1"):
        self.id = call_id
        self.function = FakeFunction(name, arguments)


class FakeMessage:
    def __init__(self, content="", tool_calls=None):
        self.content = content
        self.tool_calls = tool_calls


class FakeChoice:
    def __init__(self, message):
        self.message = message


class FakeResponse:
    def __init__(self, message):
        self.choices = [FakeChoice(message)]


class FakeBrain:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def generate_response(self, messages, tools=None):
        self.calls.append({"messages": messages, "tools": tools})
        return self.responses.pop(0)


class FakeRegistry:
    def __init__(self):
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "lookup_status",
                    "description": "Lookup status",
                    "parameters": {"type": "object", "properties": {}, "required": []},
                },
            }
        ]

    def get_tools_schema(self):
        return self.tools

    def get_function(self, name):
        if name == "lookup_status":
            return lambda: "all systems nominal"
        return None


class JarvisEngineBrainRoutingTests(unittest.TestCase):
    def test_plain_response_uses_configured_brain_manager(self):
        brain = FakeBrain([FakeResponse(FakeMessage(content="hello"))])
        engine = JarvisEngine(FakeRegistry(), brain=brain)

        result = engine.run_conversation("say hello")

        self.assertEqual(result, "hello")
        self.assertEqual(len(brain.calls), 1)
        self.assertEqual(brain.calls[0]["tools"], FakeRegistry().tools)

    def test_tool_response_finishes_through_same_brain_manager(self):
        tool_call = FakeToolCall("lookup_status", "{}")
        brain = FakeBrain(
            [
                FakeResponse(FakeMessage(tool_calls=[tool_call])),
                FakeResponse(FakeMessage(content="All systems are nominal.")),
            ]
        )
        engine = JarvisEngine(FakeRegistry(), brain=brain)

        result = engine.run_conversation("check status")

        self.assertEqual(result, "All systems are nominal.")
        self.assertEqual(len(brain.calls), 2)
        self.assertEqual(brain.calls[1]["messages"][-1]["role"], "tool")
        self.assertEqual(brain.calls[1]["messages"][-1]["content"], "all systems nominal")


if __name__ == "__main__":
    unittest.main()
