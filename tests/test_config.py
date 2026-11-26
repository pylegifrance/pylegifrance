from pylegifrance.config import (
    PROD_API_URL,
    PROD_TOKEN_URL,
    SANDBOX_API_URL,
    SANDBOX_TOKEN_URL,
    ApiConfig,
)


def test_from_env_defaults_to_production(monkeypatch):
    """PISTE_ENV is new; callers who upgrade without setting it must keep
    getting the same production endpoints from_env() always returned
    before PISTE_ENV existed, not silently switch to sandbox."""
    monkeypatch.setenv("LEGIFRANCE_CLIENT_ID", "id")
    monkeypatch.setenv("LEGIFRANCE_CLIENT_SECRET", "secret")
    monkeypatch.delenv("PISTE_ENV", raising=False)
    config = ApiConfig.from_env()
    assert config.token_url == PROD_TOKEN_URL
    assert config.api_url == PROD_API_URL


def test_from_env_sandbox_opt_in(monkeypatch):
    monkeypatch.setenv("LEGIFRANCE_CLIENT_ID", "id")
    monkeypatch.setenv("LEGIFRANCE_CLIENT_SECRET", "secret")
    monkeypatch.setenv("PISTE_ENV", "sandbox")
    config = ApiConfig.from_env()
    assert config.token_url == SANDBOX_TOKEN_URL
    assert config.api_url == SANDBOX_API_URL
