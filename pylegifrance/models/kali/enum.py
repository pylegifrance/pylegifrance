from enum import StrEnum


class TypeChampKali(StrEnum):
    """Champs de recherche disponibles pour le fond KALI.

    Restreint à la liste documentée dans
    ``docs/raw/legifrance/description-des-tris-et-filtres-de-l-api.md``
    (section KALI). ``TypeChamp`` généré contient d'autres valeurs valides
    pour d'autres fonds mais non acceptées par la recherche KALI.
    """

    ALL = "ALL"
    TITLE = "TITLE"
    IDCC = "IDCC"
    MOTS_CLES = "MOTS_CLES"
    ARTICLE = "ARTICLE"


class SortKali(StrEnum):
    """Options de tri pour les recherches dans le fond KALI."""

    PERTINENCE = "PERTINENCE"
    SIGNATURE_DATE_DESC = "SIGNATURE_DATE_DESC"
    SIGNATURE_DATE_ASC = "SIGNATURE_DATE_ASC"
    MODIFICATION_DATE_DESC = "MODIFICATION_DATE_DESC"


class FacettesKALI(StrEnum):
    """Facettes de filtrage documentées pour le fond KALI.

    Sous-ensemble minimal couvrant les usages courants (état juridique,
    IDCC, plages de dates). Les autres facettes documentées
    (``ACTIVITE``, ``NUM_TEXTE_CITE``...) peuvent être ajoutées à la
    demande.
    """

    LEGAL_STATUS = "LEGAL_STATUS"
    ARTICLE_LEGAL_STATUS = "ARTICLE_LEGAL_STATUS"
    IDCC = "IDCC"
    DATE_SIGNATURE = "DATE_SIGNATURE"
    DATE_PUBLICATION = "DATE_PUBLICATION"
