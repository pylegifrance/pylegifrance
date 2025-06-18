from enum import Enum


class NomCode(str, Enum):
    """Énumération des noms officiels des codes juridiques français."""

    CC = "Code civil"
    CCOM = "Code de commerce"
    CPD = "Code pénal"
    CDC = "Code des communes"
    CDU = "Code de l'urbanisme"
    CDDDA = "Code de déontologie des architectes"
    CDJA = "Code de justice administrative"
    CDJM = "Code de justice militaire (nouveau)"
    CDSEDF = "Code de l'action sociale et des familles"
    CD = "Code de l'énergie"
    CDEDSDEEDD = "Code de l'entrée et du séjour des étrangers et du droit d'asile"
    CDPCP = "Code de l'expropriation pour cause d'utilité publique"
    CDJ = "Code de l'organisation judiciaire"
    CDLCP = "Code de la commande publique"
    CDLC = "Code de la consommation"
    CDLCED = "Code de la construction et de l'habitation"
    CDLD = "Code de la défense"
    CDLFEDS = "Code de la famille et de l'aide sociale"
    CDLJPDM = "Code de la justice pénale des mineurs"
    CDLLDLMMEDNDM = "Code de la Légion d'honneur, de la Médaille militaire et de l'ordre national du Mérite"
    CDLM = "Code de la mutualité"
    CDLPI = "Code de la propriété intellectuelle"
    CDLR = "Code de la route"
    CDLSP = "Code de la santé publique"
    CDLSI = "Code de la sécurité intérieure"
    CDLSS = "Code de la sécurité sociale"
    CDLVR = "Code de la voirie routière"
    CDPC = "Code des procédures civiles d'exécution"
    CDPP = "Code de procédure pénale"
    CDA = "Code des assurances"
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
    CDPEDCE = "Code des postes et des communications électroniques"
    CDRELPE = "Code des relations entre le public et l'administration"
    CDT = "Code du travail"
    CDEPDLMM = "Code disciplinaire et pénal de la marine marchande"
    CDCEDA = "Code du cinéma et de l'image animée"
    CDDD = "Code du domaine de l'Etat"
    CDDDEDCPAALCTDM = "Code du domaine de l'Etat et des collectivités publiques applicable à la collectivité territoriale de Mayotte"
    CDDPFEDLNI = "Code du domaine public fluvial et de la navigation intérieure"
    CDP = "Code du patrimoine"
    CDSN = "Code du service national"
    CDS = "Code du sport"
    CDTM = "Code du travail maritime"
    CF = "Code forestier (nouveau)"
    CGDLFP = "Code général de la fonction publique"
    CGDLPDPP = "Code général de la propriété des personnes publiques"
    CGDCT = "Code général des collectivités territoriales"
    CGDI = "Code général des impôts"
    CGDAI = "Code général des impôts, annexe IV"
    CM = "Code minier (nouveau)"
    CMEF = "Code monétaire et financier"
    CP = "Code pénitentiaire"
    CR = "Code rural (ancien)"
    CREDLPM = "Code rural et de la pêche maritime"
    CE = "Code électoral"
    LDPF = "Livre des procédures fiscales"


class TypeChampCode(str, Enum):
    """Types de champs de recherche disponibles pour le fond CODE.

    Définit les différents types de champs sur lesquels effectuer une recherche
    textuelle dans les codes juridiques. Chaque type cible une partie spécifique
    du document juridique.

    Args:
        Les valeurs correspondent aux identifiants techniques des types de champs
        reconnus par l'API de recherche dans le fond CODE.

    Examples:
        Recherche dans tous les champs:
            >>> type_champ = TypeChampCode.ALL
            >>> # Usage: {"typeChamp": "ALL", "criteres": [...]}

        Recherche par numéro d'article:
            >>> type_champ = TypeChampCode.NUM_ARTICLE
            >>> # Usage: {"typeChamp": "NUM_ARTICLE", "criteres": [{"valeur": "L36-11"}]}

        Recherche dans le titre:
            >>> type_champ = TypeChampCode.TITLE
            >>> # Usage: {"typeChamp": "TITLE", "criteres": [{"valeur": "droit pénal"}]}

    Note:
        Spécifique au fond CODE. D'autres fonds (LODA) peuvent avoir des types
        de champs différents. Le type ALL permet une recherche transversale
        sur l'ensemble des champs disponibles.

    Attributes:
        ALL: Recherche dans tous les champs disponibles (recherche globale)
        TITLE: Recherche dans le titre des textes et articles
        TABLE: Recherche dans les tables des matières et index
        NUM_ARTICLE: Recherche par numéro d'article spécifique (ex: "L36-11", "R123-4")
        ARTICLE: Recherche dans le contenu textuel des articles
    """

    ALL = "ALL"
    TITLE = "TITLE"
    TABLE = "TABLE"
    NUM_ARTICLE = "NUM_ARTICLE"
    ARTICLE = "ARTICLE"


class SortCode(str, Enum):
    """Options de tri pour les recherches dans le fond CODE."""

    PERTINENCE = "PERTINENCE"
    DATE_DESC = "DATE_DESC"
    DATE_ASC = "DATE_ASC"
