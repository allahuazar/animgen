import os

from openai import OpenAI

from . import config

GROQ_BASE_URL = "https://api.groq.com/openai/v1"


def _get_client(api_key_var: str, model_var: str) -> tuple[OpenAI, str]:
    key = os.environ.get(api_key_var)
    if not key:
        raise ValueError(
            f"{api_key_var} not set. Copy .env.example to .env and add your key."
        )
    model = os.environ.get(model_var, "openai/gpt-oss-20b")
    return OpenAI(api_key=key, base_url=GROQ_BASE_URL), model


def get_router_client() -> tuple[OpenAI, str]:
    return _get_client(config.GROQ_ROUTER_API_KEY_ENV, config.GROQ_ROUTER_MODEL_ENV)


def get_manim_client() -> tuple[OpenAI, str]:
    return _get_client(config.GROQ_MANIM_API_KEY_ENV, config.GROQ_MANIM_MODEL_ENV)


def get_repair_client() -> tuple[OpenAI, str]:
    return _get_client(config.GROQ_REPAIR_API_KEY_ENV, config.GROQ_REPAIR_MODEL_ENV)
