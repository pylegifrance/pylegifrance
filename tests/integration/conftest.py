"""Shared fixtures for live-API integration tests.

Three layers of PISTE rate-limiting, applied autouse to every
integration test:

1. **Per-call throttle** — 200ms sleep before each HTTP call made
   through :meth:`LegifranceClient.call_api`. Spaces intra-test API
   bursts (e.g. LODA scenarios fire many calls per test).
2. **Retry on 401 / timeout** — on a ``HTTP 401`` or ``ReadTimeout``,
   the wrapper sleeps 2s and retries once. This absorbs the very short
   throttle windows where PISTE refuses a token that was valid a
   moment ago.
3. **Per-test pause** — 500ms sleep after each test to let the token
   window refresh between tests.

Together these keep ``HTTP 401 {"error":"invalid_client"}`` below a
noise floor on the shared CI runner. Live throttling is test-only; unit
tests mock :class:`LegifranceClient` so they are unaffected.
"""

import time

import pytest

from pylegifrance.client import LegifranceClient

_PISTE_PER_CALL_DELAY_SECONDS = 0.2
_PISTE_RETRY_BACKOFF_SECONDS = 2.0
_PISTE_PER_TEST_DELAY_SECONDS = 0.5
_RETRY_MARKERS: tuple[str, ...] = ("401", "ReadTimeout", "read timeout")


@pytest.fixture(autouse=True)
def _throttle_piste_calls(monkeypatch: pytest.MonkeyPatch):
    """Throttle + one-shot retry on flaky PISTE responses.

    Patches both :meth:`LegifranceClient.call_api` (used by the fond
    façades) and :meth:`LegifranceClient.ping` (used by BDD ``Given``
    preconditions and :mod:`tests.test_client`). Without the ping
    patch, the very first step of many BDD scenarios fails whenever
    PISTE's throttle is active.
    """
    original_call_api = LegifranceClient.call_api
    original_ping = LegifranceClient.ping

    def throttled_call_api(self, route, data):
        time.sleep(_PISTE_PER_CALL_DELAY_SECONDS)
        try:
            return original_call_api(self, route, data)
        except Exception as exc:
            message = str(exc)
            if not any(marker in message for marker in _RETRY_MARKERS):
                raise
            time.sleep(_PISTE_RETRY_BACKOFF_SECONDS)
            return original_call_api(self, route, data)

    def retrying_ping(self, route="consult/ping"):
        time.sleep(_PISTE_PER_CALL_DELAY_SECONDS)
        if original_ping(self, route):
            return True
        time.sleep(_PISTE_RETRY_BACKOFF_SECONDS)
        return original_ping(self, route)

    monkeypatch.setattr(LegifranceClient, "call_api", throttled_call_api)
    monkeypatch.setattr(LegifranceClient, "ping", retrying_ping)
    yield
    time.sleep(_PISTE_PER_TEST_DELAY_SECONDS)
