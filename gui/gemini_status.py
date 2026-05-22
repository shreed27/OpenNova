READY_COLOR = "#00FFFF"
UNAVAILABLE_COLOR = "#FFA500"
CHECKING_COLOR = "#FFFFFF"


def build_gemini_live_status(startup_error):
    if startup_error:
        return {
            "label": "GEMINI LIVE: UNAVAILABLE",
            "color": UNAVAILABLE_COLOR,
            "detail": startup_error,
        }

    return {
        "label": "GEMINI LIVE: READY",
        "color": READY_COLOR,
        "detail": "Gemini Live preflight passed. Live vision is ready to launch.",
    }
