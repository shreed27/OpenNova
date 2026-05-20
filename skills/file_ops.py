import os
import json
from typing import List, Dict, Any, Callable
from core.permissions import confirmation_required, confirmation_response
from core.skill import Skill

class FileSkill(Skill):
    def __init__(self, desktop_path: str = None):
        self.desktop_path = os.path.realpath(
            desktop_path or os.path.join(os.path.expanduser("~"), "Desktop")
        )

    @property
    def name(self) -> str:
        return "file_skill"

    def get_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "manage_file",
                    "description": "Create, read, write, or append to files on the Desktop.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "action": {"type": "string", "enum": ["read", "write", "create", "append"]},
                            "filename": {"type": "string"},
                            "content": {"type": "string"},
                            "confirm": {"type": "boolean"}
                        },
                        "required": ["action", "filename"]
                    }
                }
            }
        ]

    def get_functions(self) -> Dict[str, Callable]:
        return {
            "manage_file": self.manage_file
        }

    def _resolve_desktop_file(self, filename: str) -> str:
        if os.path.isabs(filename):
            raise ValueError("Only Desktop-relative filenames are allowed.")

        filepath = os.path.realpath(os.path.join(self.desktop_path, filename))
        if filepath != self.desktop_path and not filepath.startswith(self.desktop_path + os.sep):
            raise ValueError("File path must stay inside the Desktop directory.")
        return filepath

    def manage_file(self, action: str, filename: str, content: str = "", confirm: bool = False):
        try:
            filepath = self._resolve_desktop_file(filename)
            
            if action == "read":
                if os.path.exists(filepath):
                    with open(filepath, 'r', encoding="utf-8") as f:
                        data = f.read()
                    return json.dumps({"status": "success", "content": data})
                else:
                    return json.dumps({"status": "error", "message": "File not found."})
            
            elif action in ["write", "create"]:
                if confirmation_required(confirm):
                    return json.dumps(confirmation_response("writing files"))
                with open(filepath, 'w', encoding="utf-8") as f:
                    f.write(content)
                return json.dumps({"status": "success", "message": f"Created {filename}."})
                
            elif action == "append":
                if confirmation_required(confirm):
                    return json.dumps(confirmation_response("appending to files"))
                with open(filepath, 'a', encoding="utf-8") as f:
                    f.write("\n" + content)
                return json.dumps({"status": "success", "message": f"Updated {filename}."})

            return json.dumps({"status": "error", "message": f"Unsupported action: {action}"})
                
        except ValueError as e:
            return json.dumps({"status": "error", "message": str(e)})
        except Exception as e:
            return json.dumps({"status": "error", "message": str(e)})
