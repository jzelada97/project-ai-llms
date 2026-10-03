"""Tests sin red: usan un modelo falso, así que no gastan cuota ni necesitan API key."""

import pytest
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage

from content_generator.generator import (
    ContentRequest,
    GenerationError,
    _friendly_error,
    generate_content,
)
from content_generator.prompts import (
    AUDIENCE_RULES,
    PLATFORM_RULES,
    PROMPT,
    prompt_variables,
)


def fake_llm(text: str = "Texto generado") -> GenericFakeChatModel:
    return GenericFakeChatModel(messages=iter([AIMessage(content=text)]))


def test_prompt_includes_platform_and_audience_rules():
    for platform in PLATFORM_RULES:
        for audience in AUDIENCE_RULES:
            vars_ = prompt_variables("IA", platform, audience, "Formal", "Corta")
            rendered = PROMPT.format(**vars_)
            assert PLATFORM_RULES[platform] in rendered
            assert AUDIENCE_RULES[audience] in rendered


def test_user_braces_do_not_break_prompt():
    vars_ = prompt_variables("{topic} {{x}}", "Blog", "General", "Formal", "Corta")
    assert "{topic} {{x}}" in PROMPT.format(**vars_)


def test_generate_content_returns_parsed_text():
    req = ContentRequest("Dormir bien", "LinkedIn", "General")
    assert generate_content(req, llm=fake_llm("  Hola  ")) == "Hola"


@pytest.mark.parametrize(
    "kwargs",
    [
        {"topic": "   "},
        {"topic": "x" * 201},
        {"topic": "ok", "extra": "y" * 301},
        {"topic": "ok", "platform": "MySpace"},
    ],
)
def test_invalid_requests_are_rejected(kwargs):
    base = {"topic": "ok", "platform": "Blog", "audience": "General"}
    with pytest.raises(GenerationError):
        generate_content(ContentRequest(**{**base, **kwargs}), llm=fake_llm())


def test_provider_errors_become_friendly_messages():
    class RateLimited(Exception):
        status_code = 429

    assert "Límite de peticiones" in str(_friendly_error(RateLimited("too many")))
    assert "API key" in str(_friendly_error(Exception("Invalid API Key")))


def test_model_failure_is_wrapped_in_generation_error():
    llm = GenericFakeChatModel(messages=iter([]))  # sin respuestas -> falla al invocar
    with pytest.raises(GenerationError):
        generate_content(ContentRequest("ok", "Blog", "General"), llm=llm)
