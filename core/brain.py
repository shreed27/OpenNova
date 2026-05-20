import os
import json
import requests
import logging
from typing import List, Dict, Any

logger = logging.getLogger("jarvis.brain")
REQUEST_TIMEOUT_SECONDS = 30

# Mock classes to mimic OpenAI/Groq response structure for core/engine.py
class MockToolCallFunction:
    def __init__(self, name: str, arguments: str):
        self.name = name
        self.arguments = arguments

class MockToolCall:
    def __init__(self, id: str, type: str, function: MockToolCallFunction):
        self.id = id
        self.type = type
        self.function = function

class MockMessage:
    def __init__(self, content: str, tool_calls: List[MockToolCall] = None):
        self.content = content
        self.tool_calls = tool_calls

class MockChoice:
    def __init__(self, message: MockMessage):
        self.message = message

class MockResponse:
    def __init__(self, content: str, tool_calls: List[MockToolCall] = None):
        self.choices = [MockChoice(MockMessage(content, tool_calls))]


class BrainManager:
    def __init__(self):
        self.brain_type = os.environ.get("JARVIS_BRAIN", "groq").lower().strip()
        logger.info("Initializing brain type: %s", self.brain_type)
        
        # Validate keys/configurations
        if self.brain_type == "groq" and not os.environ.get("GROQ_API_KEY"):
            logger.warning("GROQ_API_KEY missing. Defaulting to Ollama local.")
            self.brain_type = "ollama"
            
        if self.brain_type == "openai" and not os.environ.get("OPENAI_API_KEY"):
            logger.warning("OPENAI_API_KEY missing. Defaulting to Ollama local.")
            self.brain_type = "ollama"
            
        if self.brain_type == "gemini" and not os.environ.get("GEMINI_API_KEY"):
            logger.warning("GEMINI_API_KEY missing. Defaulting to Ollama local.")
            self.brain_type = "ollama"

    @staticmethod
    def response_from_openai_payload(res_data: Dict[str, Any]) -> MockResponse:
        choice = res_data["choices"][0]
        msg = choice["message"]
        content = msg.get("content") or ""

        tool_calls = None
        if "tool_calls" in msg and msg["tool_calls"]:
            tool_calls = []
            for tc in msg["tool_calls"]:
                func = MockToolCallFunction(tc["function"]["name"], tc["function"]["arguments"])
                tool_calls.append(MockToolCall(tc["id"], tc["type"], func))

        return MockResponse(content, tool_calls)

    def generate_response(self, messages: List[Dict[str, str]], tools: List[Dict[str, Any]] = None) -> Any:
        """
        Sends chat conversation to the active brain, supporting tool definitions.
        Returns a response object with choice[0].message structure.
        """
        if self.brain_type == "groq":
            return self._call_groq(messages, tools)
        elif self.brain_type == "openai":
            return self._call_openai(messages, tools)
        elif self.brain_type == "gemini":
            return self._call_gemini(messages, tools)
        elif self.brain_type == "ollama":
            return self._call_ollama(messages, tools)
        else:
            raise ValueError(f"Unknown brain type: {self.brain_type}")

    def _call_groq(self, messages: List[Dict[str, str]], tools: List[Dict[str, Any]]) -> Any:
        from groq import Groq
        client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        model_name = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
        
        kwargs = {
            "model": model_name,
            "messages": messages,
            "max_tokens": 250
        }
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"
            
        return client.chat.completions.create(**kwargs)

    def _call_openai(self, messages: List[Dict[str, str]], tools: List[Dict[str, Any]]) -> Any:
        api_key = os.environ.get("OPENAI_API_KEY")
        model_name = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model_name,
            "messages": messages,
            "max_tokens": 250
        }
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
            
        r = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        r.raise_for_status()
        return self.response_from_openai_payload(r.json())

    def _call_gemini(self, messages: List[Dict[str, str]], tools: List[Dict[str, Any]]) -> Any:
        """
        Uses dynamic importing of google-genai to generate text and parse tools.
        """
        api_key = os.environ.get("GEMINI_API_KEY")
        model_name = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
        
        try:
            from google import genai
            from google.genai import types
            
            client = genai.Client(api_key=api_key)
            
            contents = []
            system_instruction = None
            
            for m in messages:
                role = m["role"]
                if role == "system":
                    system_instruction = m["content"]
                else:
                    gemini_role = "user" if role == "user" else "model"
                    contents.append(types.Content(
                        role=gemini_role,
                        parts=[types.Part.from_text(text=m["content"])]
                    ))
            
            gemini_tools = None
            if tools:
                declarations = []
                for t in tools:
                    func = t["function"]
                    props = {}
                    required = func.get("parameters", {}).get("required", [])
                    
                    for p_name, p_schema in func.get("parameters", {}).get("properties", {}).items():
                        p_type = p_schema.get("type", "string").upper()
                        p_type_enum = getattr(types.Type, p_type, types.Type.STRING)
                        
                        props[p_name] = types.Schema(
                            type=p_type_enum,
                            description=p_schema.get("description", "")
                        )
                        
                    decl = types.FunctionDeclaration(
                        name=func["name"],
                        description=func["description"],
                        parameters=types.Schema(
                            type=types.Type.OBJECT,
                            properties=props,
                            required=required
                        )
                    )
                    declarations.append(decl)
                
                gemini_tools = [types.Tool(function_declarations=declarations)]
            
            config = types.GenerateContentConfig(
                max_output_tokens=250,
                system_instruction=system_instruction,
                tools=gemini_tools
            )
            
            response = client.models.generate_content(
                model=model_name,
                contents=contents,
                config=config
            )
            
            content = response.text or ""
            tool_calls = None
            
            if response.function_calls:
                tool_calls = []
                for idx, fc in enumerate(response.function_calls):
                    args_str = json.dumps(fc.args) if fc.args else "{}"
                    func = MockToolCallFunction(fc.name, args_str)
                    tool_calls.append(MockToolCall(f"gemini_tc_{idx}", "function", func))
                    
            return MockResponse(content, tool_calls)
            
        except Exception as e:
            logger.warning("Gemini SDK call failed; falling back to REST API: %s", e)
            return self._call_gemini_rest(messages, tools)

    def _call_gemini_rest(self, messages: List[Dict[str, str]], tools: List[Dict[str, Any]]) -> Any:
        api_key = os.environ.get("GEMINI_API_KEY")
        model_name = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
        
        headers = {
            "Content-Type": "application/json"
        }
        payload = {
            "model": model_name,
            "messages": messages,
            "max_tokens": 250
        }
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
            
        url = f"https://generativelanguage.googleapis.com/v1beta/openai/chat/completions?key={api_key}"
        r = requests.post(url, headers=headers, json=payload, timeout=REQUEST_TIMEOUT_SECONDS)
        r.raise_for_status()
        return self.response_from_openai_payload(r.json())

    def _call_ollama(self, messages: List[Dict[str, str]], tools: List[Dict[str, Any]]) -> Any:
        url = "http://localhost:11434/api/chat"
        model_name = os.environ.get("OLLAMA_MODEL", "llama3")
        
        payload = {
            "model": model_name,
            "messages": messages,
            "stream": False,
            "options": {"num_predict": 250}
        }
        if tools:
            payload["tools"] = tools
            
        try:
            r = requests.post(url, json=payload, timeout=15)
            r.raise_for_status()
            res_data = r.json()
            
            msg = res_data["message"]
            content = msg.get("content") or ""
            
            tool_calls = None
            if "tool_calls" in msg:
                tool_calls = []
                for idx, tc in enumerate(msg["tool_calls"]):
                    func = MockToolCallFunction(tc["function"]["name"], json.dumps(tc["function"]["arguments"]))
                    tool_calls.append(MockToolCall(f"ollama_tc_{idx}", "function", func))
                    
            return MockResponse(content, tool_calls)
        except Exception as e:
            logger.warning("Ollama connection failed: %s", e)
            return MockResponse("Error: Could not connect to local Ollama. Please make sure Ollama is running.", None)
