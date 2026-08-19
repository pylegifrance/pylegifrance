"""Unit tests for date conversion in ArticleFetcher."""

import time
from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError

from pylegifrance.fonds.code import ArticleFetcher


class TestArticleFetcherEpochMs:
    """Légifrance transmet les dates en millisecondes epoch, donc en UTC.
    Converties en heure locale, elles décalent la date civile d'un jour dans
    tout fuseau négatif : 1577836800000 (2020-01-01T00:00:00Z) devient
    2019-12-31 à New York. Les versions d'un article changeant à minuit, la
    requête porte alors sur la mauvaise version.
    """

    def test_epoch_ms_converted_as_utc(self, monkeypatch):
        monkeypatch.setenv("TZ", "America/New_York")
        time.tzset()

        client = MagicMock()
        fetcher = ArticleFetcher(client, "LEGIARTI000006419292")

        # La réponse mockée n'est pas exploitable : seule la requête compte.
        with pytest.raises(ValidationError):
            fetcher.at(1577836800000)

        request_data = client.call_api.call_args[0][1]
        assert request_data["date"] == "2020-01-01"
