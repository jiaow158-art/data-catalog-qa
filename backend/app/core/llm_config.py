"""In-memory LLM configuration that can be set at runtime via API.

This allows the frontend to configure LLM settings without restarting the server.
The runtime config takes precedence over .env / Settings values.
"""

_runtime: dict[str, str] = {}


def get_llm_config() -> dict[str, str]:
    """Return a copy of the current runtime LLM config."""
    return dict(_runtime)


def set_llm_config(data: dict[str, str]) -> None:
    """Update runtime LLM config. Only non-empty values are stored."""
    for key in ("api_key", "base_url", "model"):
        if key in data and data[key]:
            _runtime[key] = data[key]


def clear_llm_config() -> None:
    """Clear all runtime config, reverting to .env values."""
    _runtime.clear()
