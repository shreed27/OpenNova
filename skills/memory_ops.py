import os
import json
import tempfile
from typing import List, Dict, Any, Callable
from core.skill import Skill

class MemorySkill(Skill):
    """Skill for persistent memory storage and retrieval."""
    
    def __init__(self):
        self.memory_file = os.environ.get("JARVIS_MEMORY_FILE") or self._default_memory_file()
        try:
            self._ensure_memory_file()
        except OSError:
            self.memory_file = self._fallback_memory_file()
            self._ensure_memory_file()

    def _default_memory_file(self) -> str:
        if os.name == "posix" and os.uname().sysname == "Darwin":
            base_dir = os.path.expanduser("~/Library/Application Support/JARVIS")
        else:
            base_dir = os.path.expanduser("~/.local/share/jarvis")
        return os.path.join(base_dir, "memory.json")

    def _fallback_memory_file(self) -> str:
        project_root = os.path.dirname(os.path.dirname(__file__))
        return os.path.join(project_root, ".jarvis", "memory.json")
    
    @property
    def name(self) -> str:
        return "memory_skill"

    def _ensure_memory_file(self):
        """Create memory file if it doesn't exist."""
        os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
        if not os.path.exists(self.memory_file):
            with open(self.memory_file, 'w', encoding="utf-8") as f:
                json.dump({}, f)

    def _load_memory(self) -> dict:
        """Load memory from file."""
        try:
            with open(self.memory_file, 'r', encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}

    def _save_memory(self, memory: dict):
        """Save memory to file."""
        directory = os.path.dirname(self.memory_file)
        os.makedirs(directory, exist_ok=True)
        fd, tmp_path = tempfile.mkstemp(prefix=".memory.", suffix=".tmp", dir=directory)
        try:
            with os.fdopen(fd, 'w', encoding="utf-8") as f:
                json.dump(memory, f, indent=2)
            os.replace(tmp_path, self.memory_file)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def get_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "remember_fact",
                    "description": "Store a piece of information in persistent memory for later recall",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "key": {
                                "type": "string",
                                "description": "A short identifier for this memory (e.g., 'favorite_color', 'birthday')"
                            },
                            "value": {
                                "type": "string",
                                "description": "The information to remember"
                            }
                        },
                        "required": ["key", "value"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "retrieve_memory",
                    "description": "Retrieve a previously stored piece of information from memory",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "item_name": {
                                "type": "string",
                                "description": "The name of the item to retrieve (e.g., 'user_name')"
                            }
                        },
                        "required": ["item_name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_all_memories",
                    "description": "List all stored memories and their keys",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "forget_fact",
                    "description": "Delete a specific memory from storage",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "key": {
                                "type": "string",
                                "description": "The identifier for the memory to delete"
                            }
                        },
                        "required": ["key"]
                    }
                }
            }
        ]

    def get_functions(self) -> Dict[str, Callable]:
        return {
            "remember_fact": self.remember_fact,
            "retrieve_memory": self.retrieve_memory,
            "list_all_memories": self.list_all_memories,
            "forget_fact": self.forget_fact
        }

    def remember_fact(self, key: str, value: str) -> str:
        """
        Store a fact in memory.
        
        Args:
            key: Memory identifier
            value: Value to store
            
        Returns:
            JSON string with status
        """
        try:
            memory = self._load_memory()
            memory[key] = value
            self._save_memory(memory)
            
            return json.dumps({
                "status": "success",
                "message": f"I will remember that {key} is {value}",
                "key": key,
                "value": value
            })
        except Exception as e:
            return json.dumps({
                "status": "error",
                "message": f"Failed to store memory: {str(e)}"
            })

    def retrieve_memory(self, item_name: str) -> str:
        """
        Retrieve a fact from memory.
        
        Args:
            item_name: Memory identifier
            
        Returns:
            JSON string with the stored value
        """
        try:
            memory = self._load_memory()
            
            if item_name in memory:
                return json.dumps({
                    "status": "success",
                    "item_name": item_name,
                    "value": memory[item_name]
                })
            else:
                return json.dumps({
                    "status": "not_found",
                    "message": f"I don't remember anything about '{item_name}'"
                })
        except Exception as e:
            return json.dumps({
                "status": "error",
                "message": f"Failed to recall memory: {str(e)}"
            })

    def list_all_memories(self) -> str:
        """
        List all stored memories.
        
        Returns:
            JSON string with all memories
        """
        try:
            memory = self._load_memory()
            
            if not memory:
                return json.dumps({
                    "status": "success",
                    "message": "I don't have any memories stored yet",
                    "memories": {}
                })
            
            return json.dumps({
                "status": "success",
                "count": len(memory),
                "memories": memory
            })
        except Exception as e:
            return json.dumps({
                "status": "error",
                "message": f"Failed to list memories: {str(e)}"
            })

    def forget_fact(self, key: str) -> str:
        """
        Delete a memory.
        
        Args:
            key: Memory identifier to delete
            
        Returns:
            JSON string with status
        """
        try:
            memory = self._load_memory()
            
            if key in memory:
                del memory[key]
                self._save_memory(memory)
                
                return json.dumps({
                    "status": "success",
                    "message": f"I have forgotten about '{key}'"
                })
            else:
                return json.dumps({
                    "status": "not_found",
                    "message": f"I don't have any memory about '{key}' to forget"
                })
        except Exception as e:
            return json.dumps({
                "status": "error",
                "message": f"Failed to forget memory: {str(e)}"
            })
