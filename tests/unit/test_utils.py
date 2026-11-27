"""Unit tests for pylegifrance.utils: EnumEncoder and
configure_session_timeouts().
"""

import enum
import json
from datetime import datetime

import pytest
import requests

from pylegifrance.config import ApiConfig
from pylegifrance.utils import EnumEncoder, configure_session_timeouts


class _Color(enum.Enum):
    RED = "red"
    BLUE = "blue"


# ---------------------------------------------------------------------------
# EnumEncoder
# ---------------------------------------------------------------------------


def test_enum_encoder_serializes_enum_to_its_value():
    payload = {"color": _Color.RED}

    result = json.dumps(payload, cls=EnumEncoder)

    assert json.loads(result) == {"color": "red"}


def test_enum_encoder_serializes_datetime_to_isoformat():
    when = datetime(2020, 1, 1, 12, 30, 0)
    payload = {"when": when}

    result = json.dumps(payload, cls=EnumEncoder)

    assert json.loads(result) == {"when": when.isoformat()}


def test_enum_encoder_falls_back_to_default_for_unsupported_type():
    class Unserializable:
        pass

    with pytest.raises(TypeError):
        json.dumps({"x": Unserializable()}, cls=EnumEncoder)


def test_enum_encoder_handles_plain_json_types_normally():
    payload = {"a": 1, "b": "text", "c": [1, 2, 3], "d": None}

    result = json.dumps(payload, cls=EnumEncoder)

    assert json.loads(result) == payload


# ---------------------------------------------------------------------------
# configure_session_timeouts()
# ---------------------------------------------------------------------------


def test_configure_session_timeouts_applies_default_timeout():
    session = requests.Session()
    config = ApiConfig(
        client_id="id", client_secret="secret", connect_timeout=1.5, read_timeout=9.0
    )

    configure_session_timeouts(session, config)

    captured = {}

    def fake_send(self, request, **kwargs):
        captured.update(kwargs)
        response = requests.Response()
        response.status_code = 200
        return response

    session.send = fake_send.__get__(session, requests.Session)
    session.get("https://example.invalid/")

    assert captured["timeout"] == (1.5, 9.0)


def test_configure_session_timeouts_does_not_override_explicit_timeout():
    session = requests.Session()
    config = ApiConfig(
        client_id="id", client_secret="secret", connect_timeout=1.5, read_timeout=9.0
    )

    configure_session_timeouts(session, config)

    captured = {}

    def fake_send(self, request, **kwargs):
        captured.update(kwargs)
        response = requests.Response()
        response.status_code = 200
        return response

    session.send = fake_send.__get__(session, requests.Session)
    session.get("https://example.invalid/", timeout=42)

    assert captured["timeout"] == 42
