"""
Constants and enumerations shared across the pylegifrance package.

This module centralizes all shared constants and enumerations to avoid duplication
and ensure consistency across the codebase.
"""

from pylegifrance.models.generated.model import TypeRecherche as _TypeRecherche
from pylegifrance.models.generated.model import Operateur as _Operateur
from pylegifrance.models.generated.model import TypeChamp as _TypeChamp
from pylegifrance.models.generated.model import Fond as _Fond
from pylegifrance.models.generated.model import Nature2 as _Nature2
from enum import Enum
from typing import Dict, List, Tuple


class CodeNom(str, Enum):
    """
    Enumeration of code names and their full titles.
    Used for code identification across the application.
    """

    # Common codes
    CCIV = "Code civil"
    CPRCIV = "Code de procédure civile"
    CCOM = "Code de commerce"
    CTRAV = "Code du travail"
    CPI = "Code de la propriété intellectuelle"
    CPEN = "Code pénal"
    CPP = "Code de procédure pénale"
    CASSUR = "Code des assurances"
    CCONSO = "Code de la consommation"
    CSI = "Code de la sécurité intérieure"
    CSP = "Code de la santé publique"
    CSS = "Code de la sécurité sociale"
    CESEDA = "Code de l'entrée et du séjour des étrangers et du droit d'asile"
    CGCT = "Code général des collectivités territoriales"
    CPCE = "Code des postes et des communications électroniques"
    CENV = "Code de l'environnement"
    CJA = "Code de justice administrative"

    # Additional codes
    CC = "Code civil"  # Alias for CCIV
    CDC = "Code des communes"
    CDDDA = "Code de déontologie des architectes"
    CDJA = "Code de justice administrative"  # Alias for CJA
    CDJM = "Code de justice militaire (nouveau)"
    CDSEDF = "Code de l'action sociale et des familles"
    CD = "Code de l'énergie"
    CDEDSDÉEDD = "Code de l'entrée et du séjour des étrangers et du droit d'asile"  # Alias for CESEDA
    CDPCP = "Code de l'expropriation pour cause d'utilité publique"
    CDJ = "Code de l'organisation judiciaire"
    CDLCP = "Code de la commande publique"
    CDLC = "Code de la consommation"  # Alias for CCONSO
    CDLCED = "Code de la construction et de l'habitation"
    CDLD = "Code de la défense"
    CDLFEDS = "Code de la famille et de l'aide sociale"
    CDLJPDM = "Code de la justice pénale des mineurs"
    CDLLDLMMEDNDM = "Code de la Légion d'honneur, de la Médaille militaire et de l'ordre national du Mérite"
    CDLM = "Code de la mutualité"
    CDLPI = "Code de la propriété intellectuelle"  # Alias for CPI
    CDLR = "Code de la route"
    CDLSP = "Code de la santé publique"  # Alias for CSP
    CDLSI = "Code de la sécurité intérieure"  # Alias for CSI
    CDLSS = "Code de la sécurité sociale"  # Alias for CSS
    CDLVR = "Code de la voirie routière"
    CDPC = "Code des procédures civiles d'exécution"
    CDPP = "Code de procédure pénale"  # Alias for CPP
    CDA = "Code des assurances"  # Alias for CASSUR
    CDCDL = "Code des communes de la Nouvelle-Calédonie"
    CDD = "Code des douanes"
    CDDDM = "Code des douanes de Mayotte"
    CDISLBES = "Code des impositions sur les biens et services"
    CDIMEDM = "Code des instruments monétaires et des médailles"
    CDJF = "Code des juridictions financières"
    CDPCEMDR = "Code des pensions civiles et militaires de retraite"
    CDPDRDMFDDPODP = "Code des pensions de retraite des marins français du commerce, de pêche ou de plaisance"
    CDPMEDVDG = "Code des pensions militaires d'invalidité et des victimes de guerre"
    CDPM = "Code des ports maritimes"
    CDPEDCÉ = "Code des postes et des communications électroniques"  # Alias for CPCE
    CDRELPE = "Code des relations entre le public et l'administration"
    CDT = "Code du travail"  # Alias for CTRAV
    CDEPDLMM = "Code disciplinaire et pénal de la marine marchande"
    CDCEDA = "Code du cinéma et de l'image animée"
    CDDD = "Code du domaine de l'Etat"
    CDDDEDCPAÀLCTDM = "Code du domaine de l'Etat et des collectivités publiques applicable à la collectivité territoriale de Mayotte"
    CDDPFEDLNI = "Code du domaine public fluvial et de la navigation intérieure"
    CDP = "Code du patrimoine"
    CDSN = "Code du service national"
    CDS = "Code du sport"
    CDTM = "Code du travail maritime"
    CF = "Code forestier (nouveau)"
    CGDLFP = "Code général de la fonction publique"
    CGDLPDPP = "Code général de la propriété des personnes publiques"
    CGDCT = "Code général des collectivités territoriales"  # Alias for CGCT
    CGDI = "Code général des impôts"
    CGDIA1 = "Code général des impôts, annexe I"
    CGDIA2 = "Code général des impôts, annexe II"
    CGDIA3 = "Code général des impôts, annexe III"
    CGDIA4 = "Code général des impôts, annexe IV"
    CGDAI = "Code général des impôts, annexe IV"
    CM = "Code minier (nouveau)"
    CM2 = "Code minier"
    CMEF = "Code monétaire et financier"
    CP = "Code pénitentiaire"
    CR = "Code rural (ancien)"
    CREDLPM = "Code rural et de la pêche maritime"
    CÉ = "Code électoral"
    LDPF = "Livre des procédures fiscales"
    CASF = "Code de l'action sociale et des familles"
    CDLU = "Code de l'urbanisme"
    CDLAR = "Code de l'artisanat"
    CDLAC = "Code de l'aviation civile"
    CDLE = "Code de l'éducation"
    CDLR = "Code de la recherche"
    CDTRANS = "Code des transports"
    CDTOUR = "Code du tourisme"



# Dictionary mapping code abbreviations to their full names
# This is kept for backward compatibility
CODE_LIST: Dict[str, str] = {
    code.name: code.value
    for code in CodeNom
    if code.name
    in [
        "CCIV",
        "CPRCIV",
        "CCOM",
        "CTRAV",
        "CPI",
        "CPEN",
        "CPP",
        "CASSUR",
        "CCONSO",
        "CSI",
        "CSP",
        "CSS",
        "CESEDA",
        "CGCT",
        "CPCE",
        "CENV",
        "CJA",
    ]
}


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

    JORF = _Fond.jorf.value
    CNIL = _Fond.cnil.value
    CETAT = _Fond.cetat.value
    JURI = _Fond.juri.value
    JUFI = _Fond.jufi.value
    CONSTIT = _Fond.constit.value
    KALI = _Fond.kali.value
    CODE_DATE = _Fond.code_date.value
    CODE_ETAT = _Fond.code_etat.value
    LODA_DATE = _Fond.loda_date.value
    LODA_ETAT = _Fond.loda_etat.value
    ALL = _Fond.all.value
    CIRC = _Fond.circ.value
    ACCO = _Fond.acco.value


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


class TypeFacettes(str, Enum):
    """
    Enumeration of facet types for filtering.
    """

    NOM_CODE = "NOM_CODE"
    DATE_SIGNATURE = "DATE_SIGNATURE"
    DATE_VERSION = "DATE_VERSION"
    TEXT_LEGAL_STATUS = "TEXT_LEGAL_STATUS"
    ARTICLE_LEGAL_STATUS = "ARTICLE_LEGAL_STATUS"
    NATURE = "NATURE"
    NOR = "NOR"


class TypeRecherche(Enum):
    """
    Enumeration of search types.
    """

    EXACTE = "EXACTE"
    APPROXIMATIVE = "APPROXIMATIVE"
    TOUS_LES_MOTS = "TOUS_LES_MOTS"
    UN_DES_MOTS = "UN_DES_MOTS"
    AUCUN_MOT = "AUCUN_MOT"
    EXPRESSION = "EXPRESSION"
    CHAMP_VIDE = "CHAMP_VIDE"
    TOUS_LES_MOTS_DANS_UN_CHAMP = "TOUS_LES_MOTS_DANS_UN_CHAMP"
    AUCUN_DES_MOTS = "AUCUN_DES_MOTS"
    AUCUNE_CORRESPONDANCE_A_CETTE_EXPRESSION = (
        "AUCUNE_CORRESPONDANCE_A_CETTE_EXPRESSION"
    )

    @classmethod
    def _missing_(cls, value):
        """Handle missing values by trying to match them to existing enum members."""
        if isinstance(value, _TypeRecherche):
            # If we get a generated enum instance, convert it to its string value
            return cls(value.value)
        return None


class Operateur(str, Enum):
    """Opérateur entre les champs de recherche.

    This enum is compatible with the generated Operateur enum.
    Using str as a base class ensures type compatibility with string literals.
    """

    ET = _Operateur.et.value
    OU = _Operateur.ou.value

    @classmethod
    def _missing_(cls, value) -> str | None:
        """Handle missing values by trying to match them to existing enum members."""
        if isinstance(value, _Operateur):
            return cls(value.value)
        return None


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


# List of deprecated routes and their replacements
# Format: (deprecated_route, replacement_route, replacement_params)
# If there are no special parameters needed for the replacement, use None
DEPRECATED_ROUTES: List[Tuple[str, str, Dict[str, str]]] = [
    ("consult/code/tableMatieres", "consult/legi/tableMatieres", {"nature": "CODE"}),
]
