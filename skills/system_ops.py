import json
import subprocess
from typing import List, Dict, Any, Callable
from core.permissions import confirmation_required, confirmation_response
from core.skill import Skill

class SystemSkill(Skill):
    @property
    def name(self) -> str:
        return "system_skill"

    def get_tools(self) -> List[Dict[str, Any]]:
        return [
             {
                "type": "function",
                "function": {
                    "name": "set_volume",
                    "description": "Set system volume (0-100)",
                    "parameters": { "type": "object", "properties": { "level": {"type": "integer"}, "confirm": {"type": "boolean"} }, "required": ["level"] }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "open_app",
                    "description": "Open an application on the computer",
                    "parameters": { "type": "object", "properties": { "app_name": {"type": "string"}, "confirm": {"type": "boolean"} }, "required": ["app_name"] }
                }
            }
        ]

    def get_functions(self) -> Dict[str, Callable]:
        return {
            "set_volume": self.set_volume,
            "open_app": self.open_app
        }

    def set_volume(self, level, confirm: bool = False):
        if confirmation_required(confirm):
            return json.dumps(confirmation_response("changing system volume"))
        try:
            level = int(level)
        except (TypeError, ValueError):
            return json.dumps({"status": "error", "message": "Volume level must be an integer from 0-100."})
        if level < 0 or level > 100:
            return json.dumps({"status": "error", "message": "Volume level must be from 0-100."})
        try:
            subprocess.run(
                ["osascript", "-e", f"set volume output volume {level}"],
                check=True,
                capture_output=True,
                text=True,
            )
            return json.dumps({"status": "success", "level": level})
        except Exception as e:
            return json.dumps({"status": "error", "message": str(e)})

    def open_app(self, app_name, confirm: bool = False):
        if confirmation_required(confirm):
            return json.dumps(confirmation_response("opening applications"))
        app_name = str(app_name).strip()
        if not app_name:
            return json.dumps({"status": "error", "message": "Application name is required."})
        try:
            subprocess.run(["open", "-a", app_name], check=True, capture_output=True, text=True)
            return json.dumps({"status": "success", "app": app_name})
        except Exception as e:
            return json.dumps({"status": "error", "message": str(e)})
