import os
import pytest
from dotenv import load_dotenv
from pylegifrance.client import LegifranceClient
from pylegifrance.config import ApiConfig


@pytest.mark.parametrize(
    "config_type,description",
    [
        ("env_vars", "client initialization with environment variables"),
        ("explicit", "client initialization with explicit configuration"),
    ],
)
def test_client_initialization(config_type, description):
    """
    Test client initialization with different configuration methods.

    Parameters
    ----------
    config_type : str
        Type of configuration to test ('env_vars' or 'explicit')
    description : str
        Description of the test case
    """
    # Given API credentials
    load_dotenv()
    client_id = os.getenv("LEGIFRANCE_CLIENT_ID", "test_client_id")
    client_secret = os.getenv("LEGIFRANCE_CLIENT_SECRET", "test_client_secret")

    # When a client is created with the specified configuration
    if config_type == "env_vars":
        client = LegifranceClient()  # Should load from environment variables by default
    else:  # explicit config
        config = ApiConfig(client_id=client_id, client_secret=client_secret)
        client = LegifranceClient(config=config)

    # Then the client should be able to make API calls
    try:
        assert client.ping(), f"Ping failed for {description}"
    finally:
        client.close()


def test_client_initialization_without_env_vars(monkeypatch):
    """
    Test that the client raises an error when environment variables are not set.
    """
    # Given no environment variables
    monkeypatch.delenv("LEGIFRANCE_CLIENT_ID", raising=False)
    monkeypatch.delenv("LEGIFRANCE_CLIENT_SECRET", raising=False)

    # Mock load_dotenv to do nothing, preventing it from loading variables from .env file
    monkeypatch.setattr("pylegifrance.config.load_dotenv", lambda: None)

    # When a client is created without explicit configuration
    # Then it should raise a ValueError
    with pytest.raises(ValueError) as excinfo:
        LegifranceClient()

    # Verify the error message
    assert "Required environment variables" in str(excinfo.value)


def test_update_api_keys_with_valid_credentials(monkeypatch):
    """
    Test that update_api_keys replaces invalid credentials with valid ones from env.
    """
    # Given invalid credentials
    bad_config = ApiConfig(client_id="fake_id", client_secret="fake_secret")
    client = LegifranceClient(config=bad_config)

    # The initial ping should fail
    with pytest.raises(Exception):
        client.ping()

    # Simulate using other credentials
    load_dotenv()
    client_id = os.getenv("LEGIFRANCE_CLIENT_ID")
    client_secret = os.getenv("LEGIFRANCE_CLIENT_SECRET")

    client.update_api_keys(client_id=client_id, client_secret=client_secret)

    # Now ping should succeed
    assert client.ping(), "Ping should succeed after updating with valid API keys"

    client.close()


def test_ping_success(api_client):
    """
    Test that the ping method correctly verifies API connectivity.
    """
    # When the ping method is called
    success = api_client.ping()

    # Then it should return True for a valid connection
    assert success is True, "Ping should return True for a valid API connection."


def test_session_context_manager():
    """
    Test the session context manager.
    """
    # Given a client configuration with real credentials
    load_dotenv()
    config = ApiConfig.from_env()

    # When using the client with a context manager
    with LegifranceClient(config=config).session_context() as client:
        # Then the client should be usable for making API calls
        assert client.ping()

    # The session should be closed after the context manager exits
    # (This is hard to test directly, but at least we can verify the context manager works)
