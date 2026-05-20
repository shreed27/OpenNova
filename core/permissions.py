import os


def trusted_mode_enabled() -> bool:
    return os.environ.get("JARVIS_TRUSTED_MODE", "").lower() in {"1", "true", "yes", "on"}


def confirmation_required(confirm: bool = False) -> bool:
    return not confirm and not trusted_mode_enabled()


def confirmation_response(action: str) -> dict:
    return {
        "status": "confirmation_required",
        "message": f"Confirmation required before {action}. Pass confirm=true or set JARVIS_TRUSTED_MODE=true.",
    }
