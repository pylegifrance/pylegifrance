"""Utility functions for the PyLegifrance package.

This module provides utility functions used across the package.
"""

import enum
import json
from datetime import datetime

import requests

from pylegifrance.config import ApiConfig


class EnumEncoder(json.JSONEncoder):
    """JSON encoder that can handle Enum objects and datetime objects."""

    def default(self, obj):
        if isinstance(obj, enum.Enum):
            return obj.value
        elif isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


def configure_session_timeouts(session: requests.Session, config: ApiConfig) -> None:
    """
    Configure default timeouts for all requests in a session.

    This function wraps the original request method to include default timeouts
    for all requests based on the provided configuration.

    Parameters
    ----------
    session : requests.Session
        The session to configure.
    config : ApiConfig
        The configuration containing timeout values.
    """
    # Store the original request method
    original_request = session.request

    # Define a wrapper function that adds the timeout
    def request_with_timeout(*args, **kwargs):
        # Add default timeout if not provided
        if "timeout" not in kwargs:
            kwargs["timeout"] = (config.connect_timeout, config.read_timeout)
        return original_request(*args, **kwargs)

    # Replace the request method with our wrapper
    session.request = request_with_timeout
