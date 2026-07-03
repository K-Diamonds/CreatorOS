from __future__ import annotations

import logging
import os

from ai_core import BaseLLMProvider, build_provider

from app.core.config import Settings

logger = logging.getLogger(__name__)

_CLOUD_HERMES_PROVIDERS = {"hermes", "hermes-local", "ollama", "openrouter"}


def resolve_llm_provider(settings: Settings) -> str:
    """Pick the runtime LLM backend.

    Local Ollama (hermes) cannot run on Vercel. When hosted there, use OpenRouter's
    Hermes model when OPENROUTER_API_KEY is set; otherwise fall back to mock.
    """
    provider = settings.llm_provider.strip().lower()
    on_vercel = bool(os.environ.get("VERCEL"))

    if on_vercel and provider in _CLOUD_HERMES_PROVIDERS:
        if settings.openrouter_api_key.strip():
            return "openrouter"
        logger.warning(
            "vercel_llm_fallback",
            extra={
                "requested_provider": provider,
                "effective_provider": "mock",
                "hint": "Set OPENROUTER_API_KEY on Vercel for cloud Hermes",
            },
        )
        return "mock"

    return provider


def build_llm_provider(settings: Settings) -> BaseLLMProvider:
    """Build the configured LLM provider for agents (coach, content writer, etc.)."""
    provider = resolve_llm_provider(settings)
    model = settings.resolved_llm_model()

    if provider == "openclaw":
        return build_provider(
            "openclaw",
            api_key=settings.openclaw_gateway_token or "local",
            model=settings.openclaw_model or model,
            api_base=f"{settings.openclaw_gateway_url.rstrip('/')}/v1/chat/completions",
        )

    if provider in {"hermes", "hermes-local", "ollama"}:
        return build_provider(
            "hermes",
            api_key="ollama",
            model=settings.ollama_model or model,
            api_base=f"{settings.ollama_base_url.rstrip('/')}/v1/chat/completions",
        )

    if provider == "openrouter":
        return build_provider(
            "openrouter",
            api_key=settings.openrouter_api_key,
            model=settings.openrouter_model or model,
            api_base="https://openrouter.ai/api/v1/chat/completions",
            extra_headers={
                "HTTP-Referer": settings.auth_url,
                "X-Title": "CreatorOS",
            },
        )

    if provider == "openai":
        return build_provider(
            "openai",
            api_key=settings.openai_api_key,
            model=settings.openai_model or model,
        )

    if provider == "mock":
        return build_provider("mock", model=model)

    return build_provider(
        provider,
        api_key=settings.openai_api_key,
        model=model,
    )
