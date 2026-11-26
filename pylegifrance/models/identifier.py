import re
from typing import ClassVar, Self


class _RegexStr(str):
    """Generic “string with regex validation” base class.

    Validates on direct construction (``__new__``) since that's the only
    way these types are ever used in this codebase (``Cid(self._decision.cid)``
    and similar) -- the legacy ``__get_validators__``/``_validate`` pydantic-v1
    hook below is never reached by direct construction and isn't wired into
    any pydantic v2 model here, so without this, no validation ever ran
    despite every call site's docstring claiming "avec validation".
    """

    _PATTERN: ClassVar[re.Pattern[str]]

    def __new__(cls, v: str) -> Self:
        if not isinstance(v, str):
            raise TypeError("value must be a string")
        if not cls._PATTERN.fullmatch(v):
            raise ValueError(f"invalid {cls.__name__} format: {v!r}")
        return super().__new__(cls, v)

    # Pydantic hook
    @classmethod
    def __get_validators__(cls):
        yield cls._validate

    @classmethod
    def _validate(cls, v: str) -> Self:
        if not isinstance(v, str):
            raise TypeError("value must be a string")
        if not cls._PATTERN.fullmatch(v):
            raise ValueError(f"invalid {cls.__name__} format: {v!r}")
        return cls(v)

    # nicer repr in logs / notebooks
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{str(self)}')"


class Cid(_RegexStr):
    """Identifiant commun Légifrance (20 chars: préfixe de 8 lettres
    majuscules -- LEGITEXT, LEGIARTI, JURITEXT, CETATEXT, JORFTEXT,
    KALICONT, KALITEXT, CNILTEXT, ACCOTEXT, CONSTEXT... -- suivi de 12
    chiffres), e.g. "LEGITEXT000006070721"."""

    _PATTERN = re.compile(r"^[A-Z]{8}\d{12}$")


class Eli(_RegexStr):
    """European Legislation Identifier."""

    _PATTERN = re.compile(r"^eli/[a-zA-Z0-9_\-/:.]+$")


class Nor(_RegexStr):
    """Numéro d'Ordre Réglementaire (NOR)."""

    _PATTERN = re.compile(r"^[A-Z]{4}[0-9]{2}[0-9]{5}[A-Z]$")
