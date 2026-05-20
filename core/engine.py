import json
import re
import logging
from typing import Any
from core.brain import BrainManager
from core.registry import SkillRegistry

logger = logging.getLogger("jarvis.engine")

class JarvisEngine:
    def __init__(self, registry: SkillRegistry, brain: Any = None):
        self.registry = registry
        self.brain = brain or BrainManager()

        self.system_instruction = (
            "You are Jarvis, a helpful and precise AI assistant. "
            "Use the provided tools to answer the user's request. "
            "When using tools, output VALID JSON arguments only. "
            "Do NOT output the tool call as XML or with an equals sign. "
            "Just use the standard tool calling format provided by the API."
        )

    def _generate_response(self, messages, tools_schema=None):
        return self.brain.generate_response(messages, tools_schema or None)

    def run_conversation(self, user_prompt: str) -> str:
        messages = [
            {"role": "system", "content": self.system_instruction},
            {"role": "user", "content": user_prompt},
        ]

        try:
            tools_schema = self.registry.get_tools_schema()
            response = self._generate_response(messages, tools_schema)
        except Exception as e:
            # Handle tool_use_failed error from Groq
            error_str = str(e)
            if "tool_use_failed" in error_str and "failed_generation" in error_str:
                try:
                    # Extract failed generation from error message (it's inside the dict string)
                    # We look for <function=NAME{ARGS}</function> pattern
                    # Updated regex to handle optional equals sign, space, or other separators: function=NAME...{ARGS}
                    match = re.search(
                        r"<function=(\w+)(?:.*?)(?=\{)(\{.*?\})<\/function>", error_str
                    )
                    if match:
                        func_name = match.group(1)
                        func_args_str = match.group(2)
                        logger.debug("Recovered failed tool call: %s with %s", func_name, func_args_str)

                        # Manually construct a tool call-like object to trigger the execution loop
                        # But wait, the loop expects response.choices[0].message.tool_calls
                        # We can just execute it here and return the result?
                        # Or reconstruct the response object?
                        # Easiest: Execute directly here

                        function_to_call = self.registry.get_function(func_name)
                        if function_to_call:
                            try:
                                args = json.loads(func_args_str)
                                res = function_to_call(**args)
                                return str(
                                    res
                                )  # Return result directly as if it was the answer
                            except Exception as exec_e:
                                return f"Error executing recovered tool: {exec_e}"
                except Exception as parse_e:
                    logger.warning("Failed to recover tool call: %s", parse_e)

            logger.error("Brain API error: %s", e)
            return "I am having trouble connecting to the brain, sir."

        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        # CASE 1: AI wants to use a tool (Action)
        if tool_calls:
            logger.debug("Executing tool call(s)")
            messages.append(response_message)

            for tool_call in tool_calls:
                function_name = tool_call.function.name
                logger.debug("AI attempting to call: %s", function_name)

                function_to_call = self.registry.get_function(function_name)

                if not function_to_call:
                    res = "Error: Tool not found."
                    logger.warning("Tool %s not found in registry", function_name)
                else:
                    try:
                        function_args = json.loads(tool_call.function.arguments)
                        logger.debug("Tool arguments: %s", function_args)

                        if function_args is None:
                            function_args = {}

                        res = function_to_call(**function_args)
                        logger.debug("Tool output: %s", str(res)[:100])
                    except Exception as e:
                        res = f"Error executing tool: {e}"
                        logger.exception("Tool execution error")

                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": str(res),
                    }
                )

            # Get final spoken response after tool runs
            second_response = self._generate_response(messages, tools_schema)
            return second_response.choices[0].message.content

        # CASE 2: AI wants to chat
        else:
            return response_message.content
