"""Unit tests for :mod:`pylegifrance.models.identifier` (Cid, Eli, Nor).

Cid's real-world shape is a fixed 8-uppercase-letter prefix (LEGITEXT,
LEGIARTI, JURITEXT, CETATEXT, JORFTEXT, KALICONT, KALITEXT, CNILTEXT,
ACCOTEXT, CONSTEXT...) followed by exactly 12 digits -- confirmed against
every real value already used elsewhere in this test suite (e.g.
"LEGITEXT000006070721", "LEGIARTI000006419292", "KALICONT000005635384")
and independently against Légifrance's own identifier scheme.
"""

from typing import Any

import pytest

from pylegifrance.models.identifier import Cid, Eli, Nor


class TestCidConstruction:
    """Direct construction -- the only way Cid is ever used in this
    codebase -- must validate, matching its "avec validation" docstrings."""

    @pytest.mark.parametrize(
        "value",
        [
            "LEGITEXT000006070721",
            "LEGIARTI000006419292",
            "JURITEXT000037999394",
            "CETATEXT000007422435",
            "KALICONT000005635384",
        ],
    )
    def test_accepts_real_shaped_values(self, value):
        cid = Cid(value)
        assert cid == value
        assert isinstance(cid, Cid)

    @pytest.mark.parametrize(
        "value",
        [
            "not-a-cid-at-all",
            "",
            "123",
            "lowercase000000000000",
            "ABC1234567890123",  # the old (wrong) 16-char pattern's shape
            "LEGITEXT00000607072",  # 11 digits, not 12
            "LEGITEXT0000060707212",  # 13 digits, not 12
            "legitext000006070721",  # lowercase prefix
        ],
    )
    def test_rejects_invalid_values(self, value):
        with pytest.raises(ValueError, match="invalid Cid format"):
            Cid(value)

    def test_rejects_non_string(self):
        non_string_value: Any = 12345
        with pytest.raises(TypeError, match="value must be a string"):
            Cid(non_string_value)


class TestEliConstruction:
    def test_accepts_eli_prefixed_value(self):
        value = "eli/jorf/2020/1/1/TREK1901124A/jo/texte"
        assert Eli(value) == value

    @pytest.mark.parametrize("value", ["", "jorf/2020/1/1", "ELI/jorf/2020"])
    def test_rejects_invalid_values(self, value):
        with pytest.raises(ValueError, match="invalid Eli format"):
            Eli(value)


class TestNorConstruction:
    def test_accepts_real_world_shaped_value(self):
        # 4 letters + 2 digits + 5 digits + 1 letter, e.g. "MTRD2011622L"
        # used in tests/unit/fonds/test_loda_fetch.py.
        assert Nor("MTRD2011622L") == "MTRD2011622L"

    @pytest.mark.parametrize(
        "value",
        [
            "",
            "mtrd2011622L",  # lowercase prefix
            "MTRD201162L",  # too short
            "MTRD2011622",  # missing trailing letter
        ],
    )
    def test_rejects_invalid_values(self, value):
        with pytest.raises(ValueError, match="invalid Nor format"):
            Nor(value)


class TestRegexStrRepr:
    def test_repr_includes_class_name_and_value(self):
        cid = Cid("LEGITEXT000006070721")
        assert repr(cid) == "Cid('LEGITEXT000006070721')"


class TestGetValidatorsHook:
    """``__get_validators__`` is a legacy pydantic-v1-style hook, never
    wired into any pydantic v2 model in this codebase (confirmed
    separately: using Cid as an annotated field on a pydantic v2
    BaseModel raises TypeError regardless of input validity, since
    pydantic v2 calls v1-style validators with an incompatible
    signature). It's unused dead code; only the generator-yield itself
    is tested here, for whichever caller might still reach it directly."""

    def test_yields_validate_classmethod(self):
        validators = list(Cid.__get_validators__())
        assert validators == [Cid._validate]
