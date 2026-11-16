import pytest

from reel_studio.core.errors import ReelError
from reel_studio.core.llm import LLMClient, parse_json


def test_parse_json_remove_cercas_markdown():
    assert parse_json('```json\n{"a": 1}\n```') == {"a": 1}


def test_parse_json_rejeita_lixo():
    with pytest.raises(ReelError):
        parse_json("não é json")


def test_llm_client_usa_sender_injetado():
    captured = {}

    def fake_send(payload):
        captured["payload"] = payload
        return '{"clips": []}'

    client = LLMClient(model="m", send=fake_send)
    out = client.complete_json("sys", "user")
    assert out == {"clips": []}
    assert captured["payload"]["model"] == "m"
    assert captured["payload"]["response_format"] == {"type": "json_object"}
