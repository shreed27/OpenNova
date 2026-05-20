import os
import json
import subprocess
from datetime import datetime
from typing import List, Dict, Any, Callable
from core.permissions import confirmation_required, confirmation_response
from core.skill import Skill

class ScreenshotSkill(Skill):
    """Skill for taking screenshots on macOS."""
    
    def __init__(self, screenshot_dir: str = None):
        # Default screenshot directory
        self.screenshot_dir = os.path.realpath(
            screenshot_dir or os.path.expanduser("~/Desktop/JARVIC_Screenshots")
        )
        # Create directory if it doesn't exist
        os.makedirs(self.screenshot_dir, exist_ok=True)
    
    @property
    def name(self) -> str:
        return "screenshot_skill"

    def get_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "take_screenshot",
                    "description": "Take a screenshot of the entire screen and save it to a file. Returns the path to the saved screenshot.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "filename": {
                                "type": "string",
                                "description": "Optional custom filename for the screenshot (without extension). If not provided, uses timestamp."
                            },
                            "confirm": {
                                "type": "boolean",
                                "description": "Set true to confirm screen capture."
                            }
                        },
                        "required": []
                    }
                }
            }
        ]

    def get_functions(self) -> Dict[str, Callable]:
        return {
            "take_screenshot": self.take_screenshot
        }

    def _resolve_screenshot_path(self, filename: str) -> str:
        if os.path.isabs(filename):
            raise ValueError("Screenshot filename must be relative to the screenshot directory.")
        filepath = os.path.realpath(os.path.join(self.screenshot_dir, filename))
        if filepath != self.screenshot_dir and not filepath.startswith(self.screenshot_dir + os.sep):
            raise ValueError("Screenshot path must stay inside the screenshot directory.")
        return filepath

    def take_screenshot(self, filename: str = None, confirm: bool = False) -> str:
        """
        Take a screenshot using macOS screencapture command.
        
        Args:
            filename: Optional custom filename (without extension)
            
        Returns:
            JSON string with status and filepath
        """
        try:
            if confirmation_required(confirm):
                return json.dumps(confirmation_response("capturing the screen"))

            # Generate filename if not provided
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}"
            
            # Ensure .png extension
            if not filename.endswith('.png'):
                filename += '.png'
            
            filepath = self._resolve_screenshot_path(filename)
            
            # Take screenshot using macOS screencapture
            # -x: no sound, -C: capture cursor
            subprocess.run(["screencapture", "-x", filepath], check=True)
            
            if os.path.exists(filepath):
                return json.dumps({
                    "status": "success",
                    "message": f"Screenshot saved successfully",
                    "path": filepath
                })
            else:
                return json.dumps({
                    "status": "error",
                    "message": "Failed to capture screenshot"
                })
                
        except ValueError as e:
            return json.dumps({
                "status": "error",
                "message": str(e)
            })
        except Exception as e:
            return json.dumps({
                "status": "error",
                "message": f"Screenshot error: {str(e)}"
            })
