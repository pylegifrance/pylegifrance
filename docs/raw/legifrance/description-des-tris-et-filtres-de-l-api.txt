
### Présentation

Ce document est un complément d'informations, à la documentation Swagger, pour la classe /search de l'API.
Il présente, par fonds :
- les champs disponibles
- Les filtres disponibles
- Les critères de tri disponibles
Recherche transverse
Journal officiel
Codes
Textes consolidés
Circulaires et instructions
Jurisprudence constitutionnelle
Jurisprudence administrative
Jurisprudence judiciaire
Jurisprudence financière
Accords de branche et conventions collectives
Accords d'entreprise
CNIL
Bulletins officiels des conventions collectives
Débats parlementaires
Questions écrites parlementaires
Documents administratifs

### ALL

Nom du champ de recherche | Champ technique et variable d'entrée
Dans tous les champs | ALL
Dans les titres | TITLE
Nom du filtre | Filtre | Variable d'entrée
fonds | origine | FOND

### JORF

Nom du champ de recherche | Champ technique et variable d'entrée
Dans tous les champs | ALL
Dans les titres | TITLE
Dans les NOR | NOR
Dans les numéros de texte | NUM
Dans les numéros d'article | NUM_ARTICLE
Dans les contenus d'article | ARTICLE
Dans les visas | VISA
Dans les notices | NOTICE
Dans les visas ou les notices | VISA_NOTICE
Dans les travaux préparatoires | TRAVAUX_PREP
Dans les signatures | SIGNATURE
Dans les notas | NOTA
Nom du filtre | Champ technique | Variable d'entrée
nature | nature | NATURE | 
date de signature | dateSignature | DATE_SIGNATURE
date de publication | datePublication | DATE_PUBLICATION
Par émetteur - ministere | ministere | MINISTERE
Par émetteur - autorité | emetteur | EMETTEUR
Numéro de NOR | nor | NOR
Numéro de texte | num | NUM_TEXTE
Numéro d'article | numArticle | NUM_ARTICLE
Décoration | decoration | DECORATION
Délégation | delegation | DELEGATION
Type de tri | Champ technique et variable d'entrée
Pertinence | PERTINENCE
Date de signature antéchronologique | SIGNATURE_DATE_DESC
Date de signature chronologique | SIGNATURE_DATE_ASC
Date de publication antéchronologique | PUBLICATION_DATE_DESC
Date de publication chronologique | PUBLICATION_DATE_ASC

### CODE

Nom du champ de recherche | Champ technique et variable d'entrée (par date) | Champ technique et variable d'entrée (par Etat)
Dans tous les champs | ALL | ALL
Dans les titres | TITLE | TITLE
Dans les tables des matières | TABLE | TABLE
Dans les numéros d'article | NUM_ARTICLE | NUM_ARTICLE
Dans les contenus d'article | ARTICLE | ARTICLE
Nom du filtre | Champ technique (par date) | Champ technique (par Etat) | Variable d'entrée (par date) | Variable d'entrée (par etat)
Etat juridique des articles |  | etatArticle |  | ARTICLE_LEGAL_STATUS
Etat juridique des textes |  | etatTexte |  | TEXT_LEGAL_STATUS
Date de la version | dateVersion |  | DATE_VERSION | 
Nom du code | nomCode | nomCode | NOM_CODE | TEXT_NOM_CODE
Numéro d'article | numArticle | numArticle | NUM_ARTICLE | NUM_ARTICLE

### LODA

Nom du champ de recherche | Champ technique et variable d'entrée (par date) | Champ technique et variable d'entrée (par Etat)
Dans tous les champs | ALL | ALL
Dans les titres | TITLE | TITLE
Dans les NOR | NOR | NOR
Dans les numéros de texte | NUM | NUM
Dans les numéros d'article | NUM_ARTICLE | NUM_ARTICLE
Dans les contenus d'article | ARTICLE | ARTICLE
Dans les visas | VISA | VISA
Dans les notices | NOTICE | NOTICE
Dans les visas ou les notices | VISA_NOTICE | VISA_NOTICE
Dans les travaux préparatoires | TRAVAUX_PREP | TRAVAUX_PREP
Dans les signatures | SIGNATURE | SIGNATURE
Dans les notas | NOTA | NOTA
Nom du filtre | Champ technique (par date) | Champ technique (par Etat) | Variable d'entrée (par date) | Variable d'entrée (par etat)
nature | nature | nature | NATURE | TEXT_NATURE
date de signature | dateSignature | dateSignature | DATE_SIGNATURE | TEXT_DATE_SIGNATURE
date de publication | datePublication | datePublication | DATE_PUBLICATION | TEXT_DATE_PUBLICATION
état juridique des articles |  | etatArticle |  | ARTICLE_LEGAL_STATUS
état juridique des textes |  | etatTexte |  | TEXT_LEGAL_STATUS
nor | nor | nor | NOR | NOR
numéro de texte | num | num | NUM_TEXTE | NUM_TEXTE
numéro d'article | numArticle | numArticle | NUM_ARTICLE | NUM_ARTICLE
date de la version | dateVersion |  | DATE_VERSION | 
Type de tri | Champ technique
Pertinence | PERTINENCE
Date de publication antéchronologique | PUBLICATION_DATE_DESC
Date de publication chronologique | PUBLICATION_DATE_ASC
Date de signature antéchronologique | SIGNATURE_DATE_DESC
Date de signature chronologique | SIGNATURE_DATE_ASC

### Circulaires

Nom du champ de recherche | Champ technique et variable d'entrée
Dans tous les champs | ALL
Dans les titres | TITLE
Dans les NOR | NOR
Dans les résumés | RESUME_CIRC
Dans les textes de référence | TEXTE_REF
Nom du filtre | Champ technique | Variable d'entrée 
Date de mise en ligne | dateMEL | DATE_MEL
Date de signature | dateSignature | DATE_SIGNATURE
Date de mise en application | dateMEA | DATE_MEA
Opposabilité | opposabilite | OPPOSABILITE
Domaine | domaine | DOMAINE
Ministère déposant | minDeposant | MIN_DEPOSANT
Ministère concerné | minConcerne | MIN_CONCERNE
Mots clés | motCle | MOTS_CLEFS
Numéro interne | numInterne | NUMERO_INTERNE
NOR | nor | NOR
Référence de publication au JO ou au BO | refPubli | REF_PUBLI
Type de tri | Champ technique
Pertinence | PERTINENCE
Date de signature antéchronologique | SIGNATURE_DATE_DESC
Date de signature chronologique | SIGNATURE_DATE_ASC
Date de mise en ligne antéchronologique | PUBLI_DATE_DESC
Date de mise en ligne chronologique | PUBLI_DATE_ASC

### CONSTIT

Nom du champ de recherche | Champ technique et variable d'entrée
Dans tous les champs | ALL
Dans les titres | TITLE
Dans les numéros de décision | NUM_DEC
Dans les contenus des textes | TEXTE
Nom du filtre | Champ technique | Variable d'entrée 
Contrôle des normes - Contrôle de constitutionnalité | natureConstit | NATURE_CONSTIT
Contrôle des normes - Autres types | natureNormeAutre | NATURE_NORME_AUTRE | 
Contrôle des normes - Type de solution | solutionConstit | SOLUTION_CONSTIT | 
Contrôle des normes - Titre de la loi déférée | titreLoi | TITRE_DEFEREE | 
Contrôle des normes - Numéro de la loi déférée | numLoi | NUM_LOI
Contrôle des normes - Date de signature | dateLoi | DATE_LOI
Contentieux électoral - Type de décision | natureElection | TYPE_DECISION
Contentieux électoral - Type de solution | solutionElect | SOLUTION_ELECT
Autres décisions - Type de décision | natureAutre | NATURE_AUTRE
Autres décisions - Type de solution | solutionAutre | SOLUTION_AUTRE
Date de décision | dateDecision | DATE_DECISION
Numéro de décision | numDecision | NUMERO_DECISION
NOR | nor | NOR
Type de tri | Champ technique
Pertinence | PERTINENCE
Date de décision antéchronologique | DATE_DESC
Date de décision chronologique | DATE_ASC

### CETAT

Nom du champ de recherche | Champ technique et variable d'entrée
Dans tous les champs | ALL
Dans les titres | TITLE
Dans les numéros de décision | NUM_DEC
Dans les abstrats | ABSTRATS
Dans les contenus des textes | TEXTE
Dans les résumés | RESUMES
Nom du filtre | Champ technique | Variable d'entrée 
Nom de la juridiction | juridiction | JURIDICTION_NATURE
Date de décision | dateDecision | DATE_DECISION | 
Date de versement dans la base | dateVersement | DATE_VERSEMENT | 
Par publication au recueil | publiRecueil | PUBLICATION_RECUEIL | 
Numéro de décision | numDecision | NUMERO_DECISION
ECLI | ecli | ECLI
Type de tri | Champ technique
Pertinence | PERTINENCE
Date de décision antéchronologique | DATE_DESC
Date de décision chronologique | DATE_ASC

### JURI

Nom du champ de recherche | Champ technique et variable d'entrée
Dans tous les champs | ALL
Dans les titres | TITLE
Dans les abstrats | ABSTRATS
Dans les numéros d'affaire | NUM_AFFAIRE
Dans les contenus des textes | TEXTE
Dans les résumés | RESUMES
Nom du filtre | Champ technique | Variable d'entrée 
Par juridiction | juridictionJudiciaire | JURIDICTION_JUDICIAIRE
Publication au bulletin | cassPubliBulletin | CASSATION_TYPE_PUBLICATION_BULLETIN | 
Numéro au bulletin | numeroBulletin | NUM_BULLETIN | 
Année ( de publication au bulletin) | anneeBulletin | ANNEE_BULLETIN |  | 
Cour de cassation - Nature de la décision | cassDecision | CASSATION_NATURE_DECISION
Cour de cassation - Formation | cassFormation | CASSATION_FORMATION
Cour de cassation - Décision attaquée | cassDecisionAttaquee | CASSATION_DECISION_ATTAQUEE
Cour de cassation - Lieu de la décision attaquée | lieuDecision | LIEU_DECISION
Cour de cassation - Date de décision attaquée | dateDecisionAttaquee | DATE_DECISION_ATTAQUEE
Juridiction d'appel - Siège de la cour | siegeAppel | APPEL_SIEGE_APPEL
Juridictions du premier degré - Type de juridiction | premiereJuri | PREMIER_DEGRE_TYPE_JURIDICTION
Juridictions du premier degré - Siège de la juridiction | siegePremierDegre | PREMIER_DEGRE_SIEGE
Date de décision | dateDecision | DATE_DECISION
Numéro d'affaire | numAffaire | NUM_AFFAIRE
ECLI | ecli | ECLI
Type de tri | Champ technique
Pertinence | PERTINENCE
Date de décision antéchronologique | DATE_DESC
Date de décision chronologique | DATE_ASC

### JUFI

Nom du champ de recherche | Champ technique et variable d'entrée
Dans tous les champs | ALL
Dans les titres | TITLE
Dans les numéros de décision | NUM_DEC
Dans les abstrats | ABSTRATS
Dans les contenus des textes | TEXTE
Nom du filtre | Champ technique | Variable d'entrée 
Par publication au recueil | publiRecueil | PUBLICATION_RECUEIL
Par juridiction | juridiction | JURIDICTION_NATURE
Date de décision | dateDecision | DATE_DECISION
Numéro de décision | numDecision | NUMERO_DECISION
Type de tri | Champ technique
Pertinence | PERTINENCE | 
Date de décision antéchronologique | DATE_DESC
Date de décision chronologique | DATE_ASC

### KALI

Nom du champ de recherche | Champ technique et variable d'entrée
Dans tous les champs | ALL
Dans les titres | TITLE
Dans les IDCC | IDCC
Dans les mots clés | MOTS_CLES
Dans les contenus des articles | ARTICLE
Nom du filtre | Champ technique | Variable d'entrée 
État juridique des textes | etatTexte | LEGAL_STATUS
État juridique des articles dans les textes | etatArticle | ARTICLE_LEGAL_STATUS | 
Par activité | activite | ACTIVITE | 
Par question usuelle | questionUsuelle | ARTICLE_QUESTION_USUELLE | 
Date de signature | dateSignature | DATE_SIGNATURE
Date de publication | datePubli | DATE_PUBLICATION
Par textes cités - Nature de texte | natureTexteCite | NATURE_TEXTE_CITE
Par textes cités - Numéro de texte | numTexteCite | NUM_TEXTE_CITE
Par textes cités - Date de publication | datePubliTexteCite | DATE_PUBLI_TEXTE_CITE
Par code cités - Nom du code | nomCodeCite | NOM_CODE_CITE
Par code cités - Numéro d'article | numArticleCite | NUM_ARTICLE_CODE_CITE
IDCC | idcc | IDCC
NOR | nor | NOR
Code NAF ou APE | codeNaf | CODE_NAF_OU_APE
Numéro de BO | numBo | NUMERO_BO
Numéro d'article | numArticle  | ARTICLE_NUMERO
Type de tri | Champ technique
Pertinence | PERTINENCE
Date de dernière modification antéchronologique | MODIFICATION_DATE_DESC
Date de signature antechronologique | SIGNATURE_DATE_DESC
Date de signature chronologique | SIGNATURE_DATE_ASC

### ACCO

Nom du champ de recherche | Champ technique et variable d'entrée
Dans tous les champs | ALL
Dans les titres | TITLE
Dans les raisons sociales | RAISON_SOCIALE
Dans les IDCC | IDCC
Nom du filtre | Champ technique | Variable d'entrée 
Thème de l'accord | theme | THEME
Nom du signataire | syndicat | SIGNATAIRE | 
Date de signature | dateSignature | DATE_SIGNATURE | 
Activité principale | activite | ACTIVITE_PRINCIPALE | 
Code APE | codeApe | CODE_APE
IDCC | idcc | IDCC
Ville de l'établissement | ville | VILLE
Code postal de l'établissement | codePostal | CODE_POSTAL
Date de publication | dateDiffusion | DATE_DIFFUSION
SIRET - Raison sociale | siret | SIRET_RAISON_SOCIALE
Type de tri | Champ technique
Pertinence | PERTINENCE
Date de signature antechronologique | DATE_DESC
Date de signature chronologique | DATE_ASC

### CNIL

Nom du champ de recherche | Champ technique et variable d'entrée
Dans tous les champs | ALL
Dans les titres | TITLE
Dans les NOR | NOR
Dans les contenus des textes | TEXTE
Dans les numéros de délibération | NUM_DELIB
Nom du filtre | Champ technique | Variable d'entrée 
Type | facetteNature | TYPE
Nature de la délibération | facetteNatureDelib | NATURE_DELIB
Date de délibération | timeInterval | DATE_DELIB
Numéro de délibération | numeroDelib | NUMERO_DELIB
NOR | nor | NOR
Type de tri | Champ technique
Pertinence | PERTINENCE
Date de décision antechronologique | DATE_DECISION_DESC
Date de décision chronologique | DATE_DECISION_ASC

### BOCC

Nom du filtre | Champ technique | Variable d'entrée 
Date de publication | intervalPublication | INTERVAL_PUBLICATION
IDCC | idcc | IDCC
Type de tri | Champ technique
Date de publication antéchronologique | BOCC_SORT_DESC
Date de publication chronologique | BOCC_SORT_ASC

### debatsParlementaires

Nom du filtre | Champ technique | Variable d'entrée 
Date de publication | dateParution | DATE_PUBLICATION
Type de publication | facetteTypePublication | TYPE_DE_PUBLICATION
Type de tri | Champ technique
Date de publication antéchronologique | DEBAT_PARLEMENTAIRE_DESC
Date de publication chronologique | DEBAT_PARLEMENTAIRE_ASC
Id croissant | ID_ASC
Id décroissant | ID_DESC

### questionsEcritesParlementaires

Nom du filtre | Champ technique | Variable d'entrée 
Date de publication | periodePublication | DATE_PUBLICATION
Type d'assemblée | facetteTypeParlement | TYPE_PARLEMENT
Type de tri | Champ technique
Date de publication antéchronologique | QUESTION_ECRITE_PARLEMENTAIRE_DESC
Date de publication chronologique | QUESTION_ECRITE_PARLEMENTAIRE_ASC
Id croissant | ID_ASC
Id décroissant | ID_DESC

### docAdmin

Nom du filtre | Champ technique | Variable d'entrée 
Années de publication | facetteYearPubli | YEARS

### Présentation du Consult

La partie suivante représente les points d'entrées du controller Consult, qui permet d'accéder aux textes et à leur contenu.
Nous allons définir les paramètres d'entrées, les champs obligatoires/ facultatifs et les valeurs possibles des champs pour les points  suivantes : 
/consult/acco
/consult/circulaire
/consult/cnil
/consult/code
/consult/code/tableMatieres
/consult/concordanceLinksArticle
/consult/debat
/consult/dossierLegislatif
/consult/eliAndAliasRedirectionTexte
/consult/getArticle
/consult/getArticleByCid
/consult/getArticleWithIdAndNum
/consult/getArticleWithIdEliOrAlias
/consult/getBoccTextPdfMetadata
/consult/getCnilWithAncienId
/consult/getCodeWithAncienId
/consult/getJoWithNor
/consult/getJuriPlanClassement
/consult/getJuriWithAncienId
/consult/getSectionByCid
/consult/getTables
/consult/jorf
/consult/jorfCont
/consult/jorfPart
/consult/juri
/consult/kaliArticle
/consult/kaliCont
/consult/kaliContIdcc
/consult/kaliSection
/consult/kaliText
/consult/lastNJo
/consult/lawDecree
/consult/legi/tableMatieres
/consult/legiPart
/consult/relatedLinksArticle
/consult/sameNumArticle

### consult-acco

Cette méthode récupère le contenu d'un accord d'entreprise à partir de son identifiant technique
Point d'entrée : /consult/acco
Nom de la variable d'entrées | Obligatoire/ facultative | Description | Valeurs possibles | Exemples
id | obligatoire | Identifiant de l'accord d'entreprise | Chaîne de caractères | ACCOTEXT000037731479
searchedString | facultative | Texte de la recherche ayant aboutie à la consultation du texte | Chaîne de caractères | constitution 1958

### consult-circulaire

Récupère le contenu d'une circulaire à partir de son identifiant technique | 
Point d'entrée: /consult/circulaire | 
Nom de la variable d'entrées | Obligatoire/ facultative | Description | Valeurs possibles | Exemples
id | obligatoire | Identifiant de la circulaire | Chaîne de caractères | 44128
searchedString | facultative | Texte de la recherche ayant aboutie à la consultation du texte | Chaîne de caractères | constitution 1958

### consult-cnil

Récupère le contenu d'un texte du fonds CNIL à partir de son identifiant technique
Point d'entrée: /consult/cnil
Nom de la variable d'entrées | Obligatoire/ facultative | Description | Valeurs possibles | Exemples
textId | obligatoire | Identifiant du texte | Chaîne de caractères | CNILTEXT000017652361
searchedString | facultative | Texte de la recherche ayant aboutie à la consultation du texte | Chaîne de caractères | constitution 1958

### consult-code

Récupère le contenu d'un texte de type CODE à partir de son identifiant et de sa date de vigueur
Point d'entrée: /consult/code
Nom de la variable d'entrées | Obligatoire/ facultative | Description | Valeurs possibles | Exemples
textId | obligatoire | Identifiant du texte | Chaîne de caractères | LEGITEXT000006075116
date | obligatoire | Date de consultation | Chaîne de caractères | 44368
searchedString | facultative | Texte de la recherche ayant aboutie à la consultation du texte | Chaîne de caractères | constitution 1958
     fromSuggest | facultative |     Variable pour savoir est-ce que la recherche est faite à partir d'une suggestion | Boolean | true
sctCid | facultative | Chronical ID de la section a consulter (Non requis pour la consultation de la table des matières sinon obligatoire) | Chaîne de caractères | LEGISCTA000006112861
abrogated | facultative | Si la section à consulter est abrogée | Boolean | true

### consult-code-tableMatieres

Récupère la table des matières d’un texte de type CODE à partir de son identifiant et de sa date de vigueur (méthode deprecated)
Point d'entrée: /consult/code/tableMatieres
Nom de la variable d'entrées | Obligatoire/ facultative | Description | Valeurs possibles | Exemples
textId  | obligatoire | Identifiant du texte | Chaîne de caractères | LEGITEXT000006075116
date | obligatoire | Date de consultation | Date | 44368
searchedString | facultative | Texte de la recherche ayant aboutie à la consultation du texte | Chaîne de caractères | constitution 1958
     fromSuggest | facultative |     Variable pour savoir est-ce que la recherche est faite à partir d'une suggestion | Boolean | true
sctCid | facultative | Chronical ID de la section a consulter (Non requis pour la consultation de la table des matières sinon obligatoire) | Chaîne de caractères | LEGISCTA000006112861
abrogated | facultative | Si la section à consulter est abrogée | Boolean | true

### consult_concordanceLinksArticl

Permet de récupérer les liens de concordance d'un article
Point d'entrée: /consult/concordanceLinksArticle
Nom de la variable d'entrées | Obligatoire/ facultative | Description | Valeurs possibles | Exemples
articleId | obligatoire | Identifiant de l'article | Chaîne de caractères | LEGIARTI000006419320

### consult-debat

Récupère le contenu d'un débat parlementaire à partir de son identifiant
Point d'entrée: /consult/debat
Nom de la variable d'entrées | Obligatoire/ facultative | Description | Valeurs possibles | Exemples
id | obligatoire | Identifiant du débat parlementaire | Chaîne de caractères | AN_2020-090.pdf

### consult-dossierLegislatif

Récupère le contenu d'un dossier legislatif par son identifiant
Point d'entrée: /consult/dossierLegislatif
Nom de la variable d'entrées | Obligatoire/ facultative | Description | Valeurs possibles | Exemples
id | obligatoire | Identifiant technique du dossier législatif | Chaîne de caractères | JORFDOLE000038049286

### consult-eliAndAliasRedirection

Récupère le contenu d'un texte du fonds JORF à partir de son idEli ou idEliAlias
Point d'entrée: /consult/eliAndAliasRedirectionTexte
Nom de la variable d'entrées | Obligatoire/ facultative | Description | Valeurs possibles | Exemples
idEliOrAlias | obligatoire | ID Eli ou Alias du JORF cible | Chaîne de caractères | /eli/decret/2018/2/13/JUSC1732516D/jo/texte

### consult-getArticle

Récupère un article par son identifiant
Point d'entrée: /consult/getArticle
Nom de la variable d'entrées | Obligatoire/ facultative | Description | Valeurs possibles | Exemples
id | obligatoire | Identifiant de l'article | Chaîne de caractères | LEGIARTI000006307920

### consult-getArticleByCid

Récupère la liste des articles par leur identifiant commun
Point d'entrée: /consult/getArticleByCid
Nom de la variable d'entrées | Obligatoire/ facultative | Description | Valeurs possibles | Exemples
cid | obligatoire | Chronical ID de l'article | Chaîne de caractères | LEGIARTI000006307920

### consult-getArticleWithIdAndNum

Récupère un Article en fonction de son  ID et Numéro article
Point d'entrée: /consult/getArticleWithIdAndNum
Nom de la variable d'entrées | Obligatoire/ facultative | Description | Valeurs possibles | Exemples
id | facultative | ID du LEGITEXT cible | Chaîne de caractères | LEGITEXT000006075116
num | facultative | Numéro de l'article cible | Chaîne de caractères | L5-8

### consult-getArticleWithIdEliOrA

Récupère un article par son identifiant Eli ou Alias
Point d'entrée: /consult/getArticleWithIdEliOrAlias
Nom de la variable d'entrées | Obligatoire/ facultative | Description | Valeurs possibles | Exemples
idEliOrAlias | obligatoire | ID Eli ou alias de l'article | Chaîne de caractères | /eli/decret/2021/7/13/PRMD2117108D/jo/article_1

### consult-getBoccTextPdfMetadata

Métadonnées d'un PDF lié à un texte unitaire BOCC
Point d'entrée: /consult/getBoccTextPdfMetadata
Nom de la variable d'entrées | Obligatoire/ facultative | Description | Valeurs possibles | Exemples
id | facultative | ID du Bocc | Chaîne de caractères | boc_20200028_0001_p000.pdf
forGlobalBocc | facultative | Si pour global Bocc | Boolean | true

### consult-getCnilWithAncienId

Récupère un texte du fond CNIL en fonction de son Ancien ID
Point d'entrée: /consult/getCnilWithAncienId
Nom de la variable d'entrées | Obligatoire/ facultative | Description | Valeurs possibles | Exemples
ancienId | facultative | Ancien Id afin de consulter un texte du fond CNIL | Chaîne de caractères | MCN97020008A

### consult-getCodeWithAncienId

Récupère un Code en fonction de son Ancien ID
Point d'entrée: /consult/getCodeWithAncienId
Nom de la variable d'entrées | Obligatoire/ facultative | Description | Valeurs possibles | Exemples
ancienId | facultative | Ancien Id afin de consulter un texte du fond CNIL | Chaîne de caractères | CASSURAL

### consult-getJoWithNor

Récupère un JO en fonction de son NOR
Point d'entrée: /consult/getJoWithNor
Nom de la variable d'entrées | Obligatoire/ facultative | Description | Valeurs possibles | Exemples
nor | obligatoire | NOR du JO cible | Chaîne de caractères | MAEJ9830052D

### consult-getJuriPlanClassement

Récupère le contenu d'un texte du fonds JURI à partir de son identifiant
Point d'entrée: /consult/getJuriPlanClassement
Nom de la variable d'entrées | Obligatoire/ facultative | Description | Valeurs possibles | Exemples
id | facultative | Identifiant du JURINOME | Chaîne de caractères | JURINOME000007644451
fond | facultative | Le fond a rechercher | Chaîne de caractères | juri
libelle | facultative | Libelle du JURINOME | Chaîne de caractères | procedure civile
     niveau | facultative | Niveau ou nous nous trouvons | Entier | 0
page | facultative | La requête ELK  | Entier | 1 (valeur par défaut)
searchSuggest | facultative | Recherche par suggestion | Boolean | false ( valeur par défaut)
searchByNiveau | facultative | Recherche par niveau | Boolean | false ( valeur par défaut)

### consult-getJuriWithAncienId

Récupère un texte du fond juri en fonction de son Ancien ID
Point d'entrée: /consult/getJuriWithAncienId
Nom de la variable d'entrées | Obligatoire/ facultative | Description | Valeurs possibles | Exemples
ancienId | facultative | Ancien Id afin de consulter un texte des fonds JURI | Chaîne de caractères | JG_L_2006_09_000000269553

### consult-getSectionByCid

Récupère la liste des section par leur identifiant commun
Point d'entrée: /consult/getSectionByCid
Nom de la variable d'entrées | Obligatoire/ facultative | Description | Valeurs possibles | Exemples
cid | obligatoire | Chronical CID de la section | Chaîne de caractères | LEGISCTA000006163288

### consult-getTables

Permet de récupérer l'ensemble des tables annuelles pour une période donnée
Point d'entrée: /consult/getTables
Nom de la variable d'entrées | Obligatoire/ facultative | Description | Valeurs possibles | Exemples
startYear | facultative | Année de début | Entier | 2012
endYear | obligatoire | Année de fin | Entier | 2017

### consult-jorf

Récupère le contenu d'un texte du fonds JORF à partir de son identifiant
Point d'entrée: /consult/jorf
Nom de la variable d'entrées | Obligatoire/ facultative | Description | Valeurs possibles | Exemples
textCid | obligatoire | Chronical ID de l'élément | Chaîne de caractères | JORFTEXT000033736934
searchedString | facultative | Texte de la recherche ayant aboutie à la consultation du texte | Chaîne de caractères | constitution 1958

### consult-jorfCont

Récupère la liste de conteneurs/sommaires JORF
Point d'entrée: /consult/jorfCont
Nom de la variable d'entrées | Obligatoire/ facultative | Description | Valeurs possibles | Exemples
id | facultative | Identifiant du conteneur JORF recherché | Chaîne de caractères | JORFCONT000022470431
num | facultative | Numéro de JORF recherché | Chaîne de caractères | 22
pageNumber | facultative | Numéro de la page à consulter | Entier | 0(valeur par défaut)
pageSize | facultative | Nombre d'éléments par page (max 100) | Entier | 0(valeur par défaut)
start.dayOfMonth | facultative | Jour | Entier | 1
start.month | facultative | Mois | Entier | 1
start.year | facultative | Année | Entier | 2012
end.dayOfMonth | facultative | Jour | Entier | 1
end.month | facultative | Mois | Entier | 1
end.year | facultative | Année | Entier | 2012
searchText | facultative | Texte à rechercher | Chaîne de caractères | mariage
date | facultative | Date de référence | Date | 1538352000000
highlightActivated | facultative | Activer/Désactiver le highlight, dans la réponse, du texte recherché | Boolean | true(valeur par défaut)

### consult-jorfPart

Récupère le contenu d'un texte du fonds JORF à partir de l'identifiant d'une de ses sections ou articles
Point d'entrée: /consult/jorfPart
Nom de la variable d'entrées | Obligatoire/ facultative | Description | Valeurs possibles | Exemples
textCid | obligatoire | Chronical ID de l'élément | Chaîne de caractères | JORFCONT000022470431
searchedString | facultative | Texte de la recherche ayant aboutie à la consultation du texte | Chaîne de caractères | constitution 1958

### consult-juri

Récupère le contenu d'un texte du fonds JURI à partir de son identifiant
Point d'entrée: /consult/juri
Nom de la variable d'entrées | Obligatoire/ facultative | Description | Valeurs possibles | Exemples
textId | obligatoire | Identifiant du texte | Chaîne de caractères | JURITEXT000037999394
searchedString | facultative | Texte de la recherche ayant aboutie à la consultation du texte | Chaîne de caractères | constitution 1958

### consult-kaliArticle

Récupère le contenu d'un texte du fonds des conventions collectives (KALI) à partir de l'identifiant de son article
Point d'entrée: /consult/kaliArticle
Nom de la variable d'entrées | Obligatoire/ facultative | Description | Valeurs possibles | Exemples
id | obligatoire | Identifiant du texte ou d'un de ses éléments enfants (section/article) | Chaîne de caractères | KALITEXT000005677408
searchedString | facultative | Texte de la recherche ayant aboutie à la consultation du texte | Chaîne de caractères | constitution 1958

###  consult-kaliCont

Récupère le contenu d'un conteneur du fonds des conventions collectives (KALI) à partir de son identifiant
Point d'entrée: /consult/kaliCont
Nom de la variable d'entrées | Obligatoire/ facultative | Description | Valeurs possibles | Exemples
id | obligatoire | Identifiant de la convention collective ou son numéro IDCC | Chaîne de caractères | KALITEXT000005677408
searchedString | facultative | Texte de la recherche ayant aboutie à la consultation du texte | Chaîne de caractères | constitution 1958

### consult-kaliContIdcc

Récupère le contenu d'un conteneur du fonds des conventions collectives (KALI) à partir de son idcc
Point d'entrée: /consult/kaliContIdcc
Nom de la variable d'entrées | Obligatoire/ facultative | Description | Valeurs possibles | Exemples
id | obligatoire | Identifiant de la convention collective ou son numéro IDCC | Chaîne de caractères | KALICONT000005635384
searchedString | facultative | Texte de la recherche ayant aboutie à la consultation du texte | Chaîne de caractères | constitution 1958

### consult-kaliSection

Récupère le contenu d'un texte du fonds des conventions collectives (KALI) à partir de l'identifiant de sa section | 
Point d'entrée: /consult/kaliSection | 
Nom de la variable d'entrées | Obligatoire/ facultative | Description | Valeurs possibles | Exemples
id | obligatoire | Identifiant du texte ou d'un de ses éléments enfants (section/article) | Chaîne de caractères | KALITEXT000005677408
searchedString | facultative | Texte de la recherche ayant aboutie à la consultation du texte | Chaîne de caractères | constitution 1958

### consult-kaliText

Récupère le contenu d'un texte du fonds des conventions collectives (KALI) à partir de son identifiant
Point d'entrée: /consult/kaliText
Nom de la variable d'entrées | Obligatoire/ facultative | Description | Valeurs possibles | Exemples
id | obligatoire | Identifiant du texte ou d'un de ses éléments enfants (section/article) | Chaîne de caractères | KALITEXT000005677408
searchedString | facultative | Texte de la recherche ayant aboutie à la consultation du texte | Chaîne de caractères | constitution 1958

### consult-lastNJo

Récupère les derniers journaux officiels
Point d'entrée: /consult/lastNJo
Nom de la variable d'entrées | Obligatoire/ facultative | Description | Valeurs possibles | Exemples
nbElement | obligatoire | Nombre de JO à remonter | Entier | 5

### consult-lawDecree

Récupère le contenu d'un texte de type LODA à partir de son identifiant et de sa date de vigueur
Point d'entrée: /consult/lawDecree
Nom de la variable d'entrées | Obligatoire/ facultative | Description | Valeurs possibles | Exemples
textId | obligatoire | Chronical ID du texte | Chaîne de caractères | LEGITEXT000006075116
date | obligatoire | Date de consultation | Date | 44301
searchedString | facultative | Texte de la recherche ayant aboutie à la consultation du texte | Chaîne de caractères | constitution 1958
fromSuggest | facultative |     Variable pour savoir est-ce que la recherche est faite à partir d'une suggestion | boolean | true

### consult-legi-tableMatieres

Récupère la table des matières d'un texte de type CODE ou LODA à partir de son identifiant, sa date de vigueur. Possibilité de rechercher uniquement les codes en positionnant 'nature' sur 'CODE'
Point d'entrée: /consult/legi/tableMatieres
Nom de la variable d'entrées | Obligatoire/ facultative | Description | Valeurs possibles | Exemples
textId | obligatoire | Chronical ID du texte | Chaîne de caractères | LEGITEXT000006075116
date | obligatoire | Date de consultation | Date | 44301
nature | facultative | Nature du texte recherché : CODE, DECRET, ARRETE, LOI, ORDONNANCE... | Chaîne de caractères | CODE

### consult-legiPart

Récupère le contenu d'un texte du fonds LEGI à partir de son identifiant et de sa date de vigueur
Point d'entrée: /consult/legiPart
Nom de la variable d'entrées | Obligatoire/ facultative | Description | Valeurs possibles | Exemples
textId | obligatoire | Chronical ID du texte | Chaîne de caractères | LEGITEXT000006075116
date | obligatoire | Date de consultation | Date | 44301
searchedString | facultative | Texte de la recherche ayant aboutie à la consultation du texte | Chaîne de caractères | constitution 1958
fromSuggest | facultative |     Variable pour savoir est-ce que la recherche est faite à partir d'une suggestion | boolean | true

### consult-relatedLinksArticle

Permet de récupérer les liens relatifs d'un article donné
Point d'entrée: /consult/relatedLinksArticle
Nom de la variable d'entrées | Obligatoire/ facultative | Description | Valeurs possibles | Exemples
articleId | obligatoire | Identifiant de l'article | Chaîne de caractères | LEGIARTI000032207188

### consult-sameNumArticle

Permet de récupérer les liens des articles ayant eu le même numéro que l'article en cours dans des versions précédentes du texte
Point d'entrée: /consult/sameNumArticle
Nom de la variable d'entrées | Obligatoire/ facultative | Description | Valeurs possibles | Exemples
textCid | obligatoire | Chronical ID du texte | Chaîne de caractères | LEGITEXT000006070721
articleCid | obligatoire | Chronical ID de l'article | Chaîne de caractères | LEGIARTI000006419319
date | obligatoire | Date de consultation | Date | 44301
articleNum | obligatoire | Numéro de l'article | Chaîne de caractères | 16