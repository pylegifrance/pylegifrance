"""
Constants and enumerations shared across the pylegifrance package.

This module centralizes all shared constants and enumerations to avoid duplication
and ensure consistency across the codebase.
"""

from pylegifrance.models.generated.model import TypeRecherche as _GeneratedTypeRecherche
from pylegifrance.models.generated.model import Operateur as _GeneratedOperateur
from pylegifrance.models.generated.model import LegalStatu as _GeneratedLegalStatu
from pylegifrance.models.generated.model import TypeChamp as _TypeChamp
from pylegifrance.models.generated.model import Fond as _GeneratedFond
from pylegifrance.models.generated.model import Nature2 as _Nature2
from enum import Enum
from typing import Dict, List, Tuple


class SupplyEnum(str, Enum):
    """
    Enumeration of supply sources for suggestions.
    Used to specify which data sources to query for suggestions.
    """

    ALL = "ALL"
    ALL_SUGGEST = "ALL_SUGGEST"
    LODA_LIST = "LODA_LIST"
    CODE_LIST = "CODE_LIST"
    CODE_RELEASE_DATE = "CODE_RELEASE_DATE"
    CODE_RELEASE_DATE_SUGGEST = "CODE_RELEASE_DATE_SUGGEST"
    CODE_LEGAL_STATUS = "CODE_LEGAL_STATUS"
    LODA_RELEASE_DATE = "LODA_RELEASE_DATE"
    LODA_RELEASE_DATE_SUGGEST = "LODA_RELEASE_DATE_SUGGEST"
    LODA_LEGAL_STATUS = "LODA_LEGAL_STATUS"
    KALI = "KALI"
    KALI_TEXT = "KALI_TEXT"
    CONSTIT = "CONSTIT"
    CETAT = "CETAT"
    JUFI = "JUFI"
    JURI = "JURI"
    JORF = "JORF"
    JORF_SUGGEST = "JORF_SUGGEST"
    CNIL = "CNIL"
    ARTICLE = "ARTICLE"
    CIRC = "CIRC"
    ACCO = "ACCO"
    PDF = "PDF"


class Fond(str, Enum):
    """Fonds de données juridiques disponibles pour la recherche Légifrance.

    Spécifie la base de données juridique dans laquelle effectuer la recherche.
    Utilisez ALL pour rechercher simultanément dans tous les fonds disponibles.

    Types de recherche spécialisés :
        Pour les fonds LODA et CODE, deux modes de recherche sont proposés :
        • _DATE : Recherche par date de version spécifique
        • _ETAT : Recherche par état juridique (en vigueur, abrogé, modifié)

    Fonds officiels disponibles :
        JORF : Journal officiel de la République française
               Textes officiels publiés au JO (lois, décrets, arrêtés, avis)

        LODA_DATE/LODA_ETAT : Base LEGI - Lois et décrets
                              Textes consolidés avec historique des versions

        CODE_DATE/CODE_ETAT : Codes juridiques
                             Codes en vigueur avec gestion des versions

        CNIL : Commission nationale de l'informatique et des libertés
               Délibérations, avis et sanctions de la CNIL

        CETAT : Conseil d'État
                Arrêts et ordonnances de la haute juridiction administrative

        JURI : Jurisprudence judiciaire
               Arrêts de la Cour de cassation et cours d'appel

        JUFI : Jurisprudence financière (bases CASS et INCA)
               Arrêts de la Cour de cassation et cours d'appel

        CONSTIT : Conseil constitutionnel
                  Décisions, avis et commentaires

        KALI : Conventions collectives nationales
               Accords et conventions du travail étendus

        CIRC : Circulaires et instructions
               Textes d'application et d'interprétation administrative

        ACCO : Accords collectifs
               Accords d'entreprise et accords de branche

        ALL : Recherche transversale
              Interrogation simultanée de tous les fonds disponibles

    Note : Les données sont mises à disposition par la DILA (Direction de
    l'information légale et administrative) via l'API Légifrance.
    """

    JORF = "JORF"
    CNIL = "CNIL"
    CETAT = "CETAT"
    JURI = "JURI"
    JUFI = "JUFI"
    CONSTIT = "CONSTIT"
    KALI = "KALI"
    CODE_DATE = "CODE_DATE"
    CODE_ETAT = "CODE_ETAT"
    LODA_DATE = "LODA_DATE"
    LODA_ETAT = "LODA_ETAT"
    ALL = "ALL"
    CIRC = "CIRC"
    ACCO = "ACCO"

    def to_generated(self) -> _GeneratedFond:
        return _GeneratedFond(self.value)

    @classmethod
    def from_generated(cls, generated: _GeneratedFond) -> "Fond":
        return cls(generated.value)


class Nature(str, Enum):
    """
    Enumeration of document nature types.
    """

    LOI = _Nature2.loi.value
    ORDONNANCE = _Nature2.ordonnance.value
    DECRET = _Nature2.decret.value
    ARRETE = _Nature2.arrete.value
    DECRET_LOI = _Nature2.decret_loi.value
    CONSTITUTION = _Nature2.constitution.value
    DECISION = _Nature2.decision.value
    CONVENTION = _Nature2.convention.value
    DECLARATION = _Nature2.declaration.value
    ACCORD_FONCTION_PUBLIQUE = _Nature2.accord_fonction_publique.value


class Facette(str, Enum):
    """Facettes de filtrage pour les recherches dans l'API juridique Légifrance.

    Définit les critères de filtrage utilisables pour affiner les recherches
    dans les différents fonds juridiques (CODE_DATE, LODA_DATE, LODA_ETAT).
    Permet de combiner plusieurs filtres pour des recherches précises et ciblées.

    Args:
        Les valeurs correspondent aux identifiants techniques des facettes
        reconnues par l'API de recherche Légifrance.

    Examples:
        Filtrage par code juridique:
            >>> facette = Facette.NOM_CODE
            >>> # Usage: {"facette": "NOM_CODE", "valeurs": ["Code civil"]}

        Filtrage par date de version:
            >>> facette = Facette.DATE_VERSION
            >>> # Usage: {"facette": "DATE_VERSION", "singleDate": 1514802418000}

        Filtrage par statut juridique:
            >>> facette = Facette.TEXT_LEGAL_STATUS
            >>> # Usage: {"facette": "TEXT_LEGAL_STATUS", "valeur": "VIGUEUR"}

        Combinaison de filtres:
            >>> filtres = [
            ...     {"facette": Facette.NOM_CODE, "valeurs": ["Code civil"]},
            ...     {"facette": Facette.DATE_VERSION, "singleDate": 1514802418000}
            ... ]

    Note:
        - Certaines facettes acceptent des valeurs multiples (valeurs: [])
        - D'autres acceptent une valeur unique (valeur: "")
        - Les facettes temporelles supportent les dates simples ou les plages
        - Compatible avec tous les fonds juridiques selon le contexte

    Attributes:
        NOM_CODE: Nom du code juridique (ex: "Code civil", "Code pénal")
        DATE_SIGNATURE: Date de signature du texte (plage ou date unique)
        DATE_VERSION: Date de version/vigueur du texte (timestamp Unix)
        TEXT_LEGAL_STATUS: Statut juridique du texte (ex: "VIGUEUR", "ABROGE")
        ARTICLE_LEGAL_STATUS: Statut juridique de l'article (ex: "VIGUEUR", "ABROGE")
        NATURE: Nature juridique du document (ex: "LOI", "DECRET", "ORDONNANCE")
        NOR: Numéro d'ordre réglementaire (identifiant administratif unique)
    """

    NOM_CODE = "NOM_CODE"
    DATE_SIGNATURE = "DATE_SIGNATURE"
    DATE_VERSION = "DATE_VERSION"
    TEXT_LEGAL_STATUS = "TEXT_LEGAL_STATUS"
    ARTICLE_LEGAL_STATUS = "ARTICLE_LEGAL_STATUS"
    NATURE = "NATURE"
    NOR = "NOR"


class TypeRecherche(str, Enum):
    """
    Enumeration of search types.
    """

    UN_DES_MOTS = "UN_DES_MOTS"
    EXACTE = "EXACTE"
    TOUS_LES_MOTS_DANS_UN_CHAMP = "TOUS_LES_MOTS_DANS_UN_CHAMP"
    AUCUN_DES_MOTS = "AUCUN_DES_MOTS"
    AUCUNE_CORRESPONDANCE_A_CETTE_EXPRESSION = (
        "AUCUNE_CORRESPONDANCE_A_CETTE_EXPRESSION"
    )
    CONTIENT = "CONTIENT"  # Added for compatibility with existing code
    EGAL = "EXACTE"  # Alias for EXACTE

    def to_generated(self) -> _GeneratedTypeRecherche:
        return _GeneratedTypeRecherche(self.value)

    @classmethod
    def from_generated(cls, generated: _GeneratedTypeRecherche) -> "TypeRecherche":
        return cls(generated.value)


class Operateur(str, Enum):
    """Opérateur entre les champs de recherche.

    This enum is compatible with the generated Operateur enum.
    Using str as a base class ensures type compatibility with string literals.
    """

    ET = "ET"
    OU = "OU"

    def to_generated(self) -> _GeneratedOperateur:
        return _GeneratedOperateur(self.value)

    @classmethod
    def from_generated(cls, generated: _GeneratedOperateur) -> "Operateur":
        return cls(generated.value)


class TypeChamp(str, Enum):
    """Type de champ.

    This enum is compatible with the generated TypeChamp enum.
    Using str as a base class ensures type compatibility with string literals.
    """

    ALL = _TypeChamp.all.value
    TITLE = _TypeChamp.title.value
    TABLE = _TypeChamp.table.value
    NOR = _TypeChamp.nor.value
    NUM = _TypeChamp.num.value
    ADVANCED_TEXTE_ID = _TypeChamp.advanced_texte_id.value
    NUM_DELIB = _TypeChamp.num_delib.value
    NUM_DEC = _TypeChamp.num_dec.value
    NUM_ARTICLE = _TypeChamp.num_article.value
    ARTICLE = _TypeChamp.article.value
    MINISTERE = _TypeChamp.ministere.value
    VISA = _TypeChamp.visa.value
    NOTICE = _TypeChamp.notice.value
    VISA_NOTICE = _TypeChamp.visa_notice.value
    TRAVAUX_PREP = _TypeChamp.travaux_prep.value
    SIGNATURE = _TypeChamp.signature.value
    NOTA = _TypeChamp.nota.value
    NUM_AFFAIRE = _TypeChamp.num_affaire.value
    ABSTRATS = _TypeChamp.abstrats.value
    RESUMES = _TypeChamp.resumes.value
    TEXTE = _TypeChamp.texte.value
    ECLI = _TypeChamp.ecli.value
    NUM_LOI_DEF = _TypeChamp.num_loi_def.value
    TYPE_DECISION = _TypeChamp.type_decision.value
    NUMERO_INTERNE = _TypeChamp.numero_interne.value
    REF_PUBLI = _TypeChamp.ref_publi.value
    RESUME_CIRC = _TypeChamp.resume_circ.value
    TEXTE_REF = _TypeChamp.texte_ref.value
    TITRE_LOI_DEF = _TypeChamp.titre_loi_def.value
    RAISON_SOCIALE = _TypeChamp.raison_sociale.value
    MOTS_CLES = _TypeChamp.mots_cles.value
    IDCC = _TypeChamp.idcc.value

    @classmethod
    def _missing_(cls, value):
        """Handle missing values by trying to match them to existing enum members."""
        if isinstance(value, _TypeChamp):
            # If we get a generated enum instance, convert it to its string value
            return cls(value.value)
        return None


class EtatJuridique(Enum):
    """Statuts juridiques des textes législatifs et réglementaires français.

    Cette énumération définit les différents états juridiques possibles pour un texte
    de loi, un article de code ou un décret dans le système juridique français,
    tels qu'utilisés par l'API Légifrance.

    Attributes:
        VIGUEUR: Texte actuellement en vigueur et applicable.
        ABROGE_DIFF: Texte abrogé avec effet différé.
        VIGUEUR_DIFF: Texte en vigueur avec effet différé.
        VIGUEUR_ETEN: Texte en vigueur étendue.
        VIGUEUR_NON_ETEN: Texte en vigueur non étendue.
        ABROGE: Texte abrogé définitivement et n'ayant plus d'effet juridique.
        PERIME: Texte périmé.
        ANNULE: Texte annulé.
        MODIFIE: Texte qui a été modifié par un texte ultérieur.
        DISJOINT: Texte disjoint.
        SUBSTITUE: Texte qui a été substitué par un autre.
        TRANSFERE: Texte transféré dans un autre code ou compilation.
        INITIALE: Version initiale d'un texte.
        MODIFIE_MORT_NE: Texte modifié mais qui n'est jamais entré en vigueur.
        SANS_ETAT: Texte sans état juridique défini.
        DENONCE: Texte dénoncé.
        REMPLACE: Texte qui a été remplacé par un autre.

    Examples:
        >>> status = EtatJuridique.VIGUEUR
        >>> generated = status.to_generated()
        >>> print(generated.value)
        'VIGUEUR'

        >>> from_api = _GeneratedLegalStatu(value='ABROGE')
        >>> status = EtatJuridique.from_generated(from_api)
        >>> print(status)
        <LegalStatus.ABROGE: 'ABROGE'>
    """

    VIGUEUR = "VIGUEUR"
    ABROGE_DIFF = "ABROGE_DIFF"
    VIGUEUR_DIFF = "VIGUEUR_DIFF"
    VIGUEUR_ETEN = "VIGUEUR_ETEN"
    VIGUEUR_NON_ETEN = "VIGUEUR_NON_ETEN"
    ABROGE = "ABROGE"
    PERIME = "PERIME"
    ANNULE = "ANNULE"
    MODIFIE = "MODIFIE"
    DISJOINT = "DISJOINT"
    SUBSTITUE = "SUBSTITUE"
    TRANSFERE = "TRANSFERE"
    INITIALE = "INITIALE"
    MODIFIE_MORT_NE = "MODIFIE_MORT_NE"
    SANS_ETAT = "SANS_ETAT"
    DENONCE = "DENONCE"
    REMPLACE = "REMPLACE"

    def to_generated(self) -> _GeneratedLegalStatu:
        """Convertit vers le type généré pour l'API.

        Returns:
            _GeneratedLegalStatu: Instance du type généré avec la valeur
                correspondante pour l'API Légifrance.
        """
        return _GeneratedLegalStatu(self.value)

    @classmethod
    def from_generated(cls, generated: _GeneratedLegalStatu) -> "EtatJuridique":
        """Crée une instance depuis le type généré de l'API.

        Args:
            generated: Instance du type généré provenant de l'API Légifrance.

        Returns:
            LegalStatus: Énumération correspondant au statut juridique.

        Raises:
            ValueError: Si la valeur du statut n'est pas reconnue.
        """
        return cls(generated.value)


class TypeFacette(str, Enum):
    """Types de facettes disponibles pour filtrer les recherches dans l'API Légifrance.

    Les facettes permettent de restreindre les résultats de recherche selon
    différents critères. Chaque facette correspond à un aspect spécifique
    des textes juridiques permettant un filtrage précis.

    Attributes:
        NOM_CODE: Nom du code juridique (ex: Code civil, Code pénal).
        DATE_SIGNATURE: Date de signature du texte juridique.
        DATE_VERSION: Date de version du texte (pour recherche historique).
        TEXT_LEGAL_STATUS: Statut juridique du texte (VIGUEUR, ABROGE, etc.).
        ARTICLE_LEGAL_STATUS: Statut juridique au niveau de l'article.
        NATURE: Nature du texte (LOI, DECRET, ARRETE, etc.).
        NOR: Numéro NOR (Numéro d'Ordre au Registre) du texte.

    Examples:
        >>> facette = TypeFacette.NOM_CODE
        >>> print(facette.value)
        'NOM_CODE'

        >>> # Utilisation dans un filtre
        >>> filtre = {
        ...     "facette": TypeFacette.DATE_VERSION.value,
        ...     "singleDate": 1514802418000
        ... }

    Note:
        Ces facettes sont utilisées dans les requêtes de recherche pour
        créer des filtres permettant de cibler précisément les textes
        juridiques souhaités. Certaines facettes sont spécifiques à
        certains fonds documentaires (CODE, LODA, JORF).
    """

    NOM_CODE = "NOM_CODE"
    DATE_SIGNATURE = "DATE_SIGNATURE"
    DATE_VERSION = "DATE_VERSION"
    TEXT_LEGAL_STATUS = "TEXT_LEGAL_STATUS"
    ARTICLE_LEGAL_STATUS = "ARTICLE_LEGAL_STATUS"
    NATURE = "NATURE"
    NOR = "NOR"


# List of deprecated routes and their replacements
# Format: (deprecated_route, replacement_route, replacement_params)
# If there are no special parameters needed for the replacement, use None
DEPRECATED_ROUTES: List[Tuple[str, str, Dict[str, str]]] = [
    ("consult/code/tableMatieres", "consult/legi/tableMatieres", {"nature": "CODE"}),
]
