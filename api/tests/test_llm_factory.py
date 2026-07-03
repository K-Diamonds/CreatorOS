import os

from app.core.config import Settings
from app.services.llm_factory import resolve_llm_provider


def _settings(**overrides: object) -> Settings:
    base = {
        "environment": "production",
        "log_level": "INFO",
        "auth_secret": "x" * 32,
        "auth_url": "https://example.com",
        "database_url": "sqlite://",
        "celery_broker_url": "redis://localhost/0",
        "celery_result_backend": "redis://localhost/1",
        "llm_provider": "hermes",
        "openrouter_api_key": "",
    }
    base.update(overrides)
    return Settings(**base)


def test_resolve_llm_provider_hermes_on_vercel_without_openrouter(monkeypatch):
    monkeypatch.setenv("VERCEL", "1")
    assert resolve_llm_provider(_settings()) == "mock"


def test_resolve_llm_provider_hermes_on_vercel_with_openrouter(monkeypatch):
    monkeypatch.setenv("VERCEL", "1")
    assert resolve_llm_provider(_settings(openrouter_api_key="sk-or-test-key-12345678")) == "openrouter"


def test_resolve_llm_provider_hermes_local_without_vercel(monkeypatch):
    monkeypatch.delenv("VERCEL", raising=False)
    assert resolve_llm_provider(_settings()) == "hermes"
