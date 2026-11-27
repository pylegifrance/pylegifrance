"""Unit tests for Code.get_article and Code._resolve_code_cid.

Direct, unambiguous current-version lookup via
/consult/getArticleWithIdAndNum, resolving the code name to its LEGITEXT cid
via /list/code first. Unlike CodeSearchBuilder.execute() with
with_legal_status(), this never has to sample/filter historical versions:
the endpoint itself only returns the currently in-force one.
"""

from unittest.mock import MagicMock

import pytest

from pylegifrance.fonds.code import Code


def _list_code_response(entries: list[dict]) -> MagicMock:
    response = MagicMock()
    response.json.return_value = {"results": entries}
    return response


def _article_response(article: dict) -> MagicMock:
    response = MagicMock()
    response.json.return_value = {"article": article}
    return response


class TestResolveCodeCid:
    def test_matches_exact_title(self):
        client = MagicMock()
        client.call_api.return_value = _list_code_response(
            [
                {"titre": "Code général des impôts", "cid": "LEGITEXT000006069577"},
                {
                    "titre": "Code général des impôts, annexe I",
                    "cid": "LEGITEXT000006069568",
                },
            ]
        )
        code = Code(client)

        cid = code._resolve_code_cid("Code général des impôts")

        assert cid == "LEGITEXT000006069577"
        endpoint, payload = client.call_api.call_args[0]
        assert endpoint == "list/code"
        assert payload["codeName"] == "Code général des impôts"

    def test_raises_when_no_exact_match(self):
        """ "/list/code" matches substrings (e.g. annexes), so an exact-title
        check is required or the wrong code's cid could be picked."""
        client = MagicMock()
        client.call_api.return_value = _list_code_response(
            [
                {
                    "titre": "Code général des impôts, annexe I",
                    "cid": "LEGITEXT000006069568",
                },
            ]
        )
        code = Code(client)

        with pytest.raises(ValueError, match="introuvable"):
            code._resolve_code_cid("Code général des impôts")

    def test_raises_when_response_falsy(self):
        client = MagicMock()
        client.call_api.return_value = None
        code = Code(client)

        with pytest.raises(ValueError, match="introuvable"):
            code._resolve_code_cid("Code civil")


class TestGetArticle:
    def test_happy_path_resolves_cid_then_fetches_current_version(self):
        client = MagicMock()
        client.call_api.side_effect = [
            _list_code_response(
                [{"titre": "Code général des impôts", "cid": "LEGITEXT000006069577"}]
            ),
            _article_response(
                {
                    "id": "LEGIARTI000053542700",
                    "num": "787 B",
                    "etat": "VIGUEUR",
                }
            ),
        ]
        code = Code(client)

        article = code.get_article("Code général des impôts", "787 B")

        assert article.id == "LEGIARTI000053542700"
        assert article.legal_status == "VIGUEUR"

        list_call, article_call = client.call_api.call_args_list
        assert list_call.args[0] == "list/code"
        assert article_call.args[0] == "consult/getArticleWithIdAndNum"
        assert article_call.args[1] == {
            "id": "LEGITEXT000006069577",
            "num": "787 B",
        }

    def test_normalizes_article_number(self):
        client = MagicMock()
        client.call_api.side_effect = [
            _list_code_response([{"titre": "Code civil", "cid": "LEGITEXT1"}]),
            _article_response({"id": "LEGIARTI1", "num": "1121-1"}),
        ]
        code = Code(client)

        code.get_article("Code civil", "L. 1121-1")

        _, article_call = client.call_api.call_args_list
        assert article_call.args[1]["num"] == "L1121-1"

    def test_raises_when_article_not_found(self):
        client = MagicMock()
        client.call_api.side_effect = [
            _list_code_response([{"titre": "Code civil", "cid": "LEGITEXT1"}]),
            None,
        ]
        code = Code(client)

        with pytest.raises(ValueError, match="non trouvé"):
            code.get_article("Code civil", "1234")

    def test_raises_when_article_is_null_in_200_response(self):
        """A nonexistent article number is a 200 OK with {"article": null},
        not a falsy response -- both must be treated as not-found."""
        client = MagicMock()
        null_article_response = MagicMock()
        null_article_response.json.return_value = {"article": None}
        client.call_api.side_effect = [
            _list_code_response([{"titre": "Code civil", "cid": "LEGITEXT1"}]),
            null_article_response,
        ]
        code = Code(client)

        with pytest.raises(ValueError, match="non trouvé"):
            code.get_article("Code civil", "L1121-1")

    def test_raises_when_code_not_found(self):
        client = MagicMock()
        client.call_api.return_value = _list_code_response([])
        code = Code(client)

        with pytest.raises(ValueError, match="introuvable"):
            code.get_article("Code inexistant", "1234")

        client.call_api.assert_called_once()
