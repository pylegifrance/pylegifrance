"""Unit tests for :mod:`pylegifrance.models.identifier` (Cid, Eli, Nor).

These tests target *actual* current behavior, not the aspirational
behavior implied by the docstrings ("string with regex validation",
"avec validation" at every call site in fonds/juri.py and fonds/loda.py).

KNOWN BUG (reported, not fixed here -- see task report for full
rationale): ``_RegexStr`` only validates through its ``_validate``
classmethod, which is solely reachable via the legacy pydantic-v1-style
``__get_validators__`` hook. Every real call site
(``Cid(self._decision.cid)`` in fonds/juri.py, ``Cid(self._texte.cid)``
in fonds/loda.py, etc.) constructs these classes *directly*, which goes
through ``str.__new__`` and performs **no validation at all** -- any
string, of any shape, is silently accepted. This directly contradicts
the class/property docstrings. A fix (validating in ``__new__``) was
prototyped and reverted: it cannot be applied without also rewriting the
``Cid._PATTERN`` regex (the existing 16-char pattern does not match any
real Legifrance CID, which are consistently 8 letters + 12 digits per
``tests/unit/fonds/test_loda_fetch.py``/``test_loda_texte.py``), and
doing so breaks ``tests/unit/fonds/test_juri_decision_extra.py``'s
``cid="JURX000037999ABC"`` fixture (a 16-char value matching only the
current, seemingly-wrong pattern) -- an out-of-scope test file this task
does not permit editing. See the task report for the full breakdown.
"""

from typing import Any

import pytest

from pylegifrance.models.identifier import Cid, Eli, Nor


class TestDirectConstructionDoesNotValidate:
    """Documents the current (buggy) behavior: direct construction -- the
    *only* way these classes are ever used in the codebase -- performs no
    validation whatsoever, despite the docstrings' claims."""

    @pytest.mark.parametrize(
        "value", ["not-a-cid-at-all", "", "123", "lowercase000000000000"]
    )
    def test_cid_accepts_any_string_on_direct_construction(self, value):
        cid = Cid(value)
        assert cid == value
        assert isinstance(cid, Cid)

    def test_eli_accepts_any_string_on_direct_construction(self):
        assert Eli("not-an-eli") == "not-an-eli"

    def test_nor_accepts_any_string_on_direct_construction(self):
        assert Nor("not-a-nor") == "not-a-nor"


class TestValidateClassmethod:
    """``_validate`` is the only code path that actually enforces
    ``_PATTERN``. It is not reachable via direct construction, but it is
    real, callable code (used by ``__get_validators__``), so it is
    tested directly against the patterns as currently defined."""

    def test_cid_validate_accepts_value_matching_current_pattern(self):
        # 3 letters + 13 alnum = 16 chars, per the current _PATTERN --
        # note this does NOT match real Legifrance CIDs (see module
        # docstring above).
        value = "ABC1234567890123"
        assert len(value) == 16
        assert Cid._validate(value) == value

    @pytest.mark.parametrize(
        "value",
        [
            "not-a-cid",
            "",
            "abc1234567890123",  # lowercase prefix
            "AB1234567890123",  # prefix too short
        ],
    )
    def test_cid_validate_rejects_invalid_values(self, value):
        with pytest.raises(ValueError, match="invalid Cid format"):
            Cid._validate(value)

    def test_cid_validate_rejects_non_string(self):
        # Deliberately an int: _validate's runtime isinstance check (not
        # its `v: str` annotation) is what's under test here, so the
        # wrong-type value is routed through an `Any`-typed local rather
        # than a `# type: ignore`, which would silently swallow any other
        # error on this line too.
        non_string_value: Any = 12345
        with pytest.raises(TypeError, match="value must be a string"):
            Cid._validate(non_string_value)

    def test_eli_validate_accepts_eli_prefixed_value(self):
        value = "eli/jorf/2020/1/1/TREK1901124A/jo/texte"
        assert Eli._validate(value) == value

    @pytest.mark.parametrize("value", ["", "jorf/2020/1/1", "ELI/jorf/2020"])
    def test_eli_validate_rejects_invalid_values(self, value):
        with pytest.raises(ValueError, match="invalid Eli format"):
            Eli._validate(value)

    def test_nor_validate_accepts_real_world_shaped_value(self):
        # 4 letters + 2 digits + 5 digits + 1 letter -- this one DOES
        # match real-world NOR values, e.g. "MTRD2011622L" used in
        # tests/unit/fonds/test_loda_fetch.py.
        assert Nor._validate("MTRD2011622L") == "MTRD2011622L"

    @pytest.mark.parametrize(
        "value",
        [
            "",
            "mtrd2011622L",  # lowercase prefix
            "MTRD201162L",  # too short
            "MTRD2011622",  # missing trailing letter
        ],
    )
    def test_nor_validate_rejects_invalid_values(self, value):
        with pytest.raises(ValueError, match="invalid Nor format"):
            Nor._validate(value)


class TestRegexStrRepr:
    def test_repr_includes_class_name_and_value(self):
        cid = Cid("LEGITEXT000006070721")
        assert repr(cid) == "Cid('LEGITEXT000006070721')"


class TestGetValidatorsHook:
    """``__get_validators__`` is a legacy pydantic-v1-style hook. It is
    never wired into any pydantic model in this codebase today (Cid/Eli/
    Nor are only ever constructed directly) -- confirmed separately: using
    Cid as an annotated field on a pydantic v2 BaseModel raises TypeError
    regardless of input validity, because pydantic v2 calls v1-style
    validators with an incompatible signature. That integration is
    unused dead code; only the generator-yield itself is tested here."""

    def test_yields_validate_classmethod(self):
        validators = list(Cid.__get_validators__())
        assert validators == [Cid._validate]
