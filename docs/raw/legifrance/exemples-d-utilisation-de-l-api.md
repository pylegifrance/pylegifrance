Utilisation de l’API Légifrance : Exemples de cas pratique

Contenu

 TOC \o "1-3" \h \z \u Utilisation de l’API Légifrance : Exemples de cas pratique PAGEREF _Toc209017031 \h 1

Contenu PAGEREF _Toc209017032 \h 1

1.Connexion OAuth PAGEREF _Toc209017033 \h 3

1.1.Obtention d’un jeton OAuth2.0 avec PISTE PAGEREF _Toc209017034 \h 3

1.2.Consommer l’API PAGEREF _Toc209017035 \h 3

2.Récupérer un article en vigueur à une date donnée, d'un code dont on connaît l'id PAGEREF _Toc209017036 \h 4

2.1.Étape 1 : Récupérer l’identifiant de l’article avec la méthode POST /search PAGEREF _Toc209017037 \h 4

2.2.Étape 2 : Récupérer le contenu de l’article avec la méthode POST /consult/getArticle PAGEREF _Toc209017038 \h 4

3.Récupérer un article en vigueur à une date donnée, d'un texte numéroté PAGEREF _Toc209017039 \h 5

3.1.Étape 1 : Trouver l’ordonnance avec la méthode POST /search PAGEREF _Toc209017040 \h 5

3.2.Étape 2 : trouver l’article de l’ordonnance avec la méthode POST /search PAGEREF _Toc209017041 \h 5

3.3.Étape 3 : Récupérer le contenu de l’article avec la méthode POST /consult/getArticle PAGEREF _Toc209017042 \h 6

4.Récupérer le texte complet d'une loi promulguée dont on connaît le n° PAGEREF _Toc209017043 \h 7

4.1.Étape 1 : Trouver l’identifiant de la loi avec la méthode POST /search PAGEREF _Toc209017044 \h 7

4.2.Étape 2 : Récupérer le contenu de la loi avec la méthode POST /consult/legiPart PAGEREF _Toc209017045 \h 7

5.Récupérer un article en vigueur à une date donnée, d'une loi identifiée par sa date de signature PAGEREF _Toc209017046 \h 8

5.1.Étape 1 : Trouver l’identifiant de la loi avec la méthode POST /search PAGEREF _Toc209017047 \h 8

5.2.Étape2 : Une fois l’identifiant LEGIARTI récupéré, on l’utilise avec la méthode /consult/getArticle PAGEREF _Toc209017048 \h 8

6.Récupérer un article en vigueur à une date donnée de la Constitution ou à défaut le texte complet de la Constitution PAGEREF _Toc209017049 \h 9

6.1.Étape 1 : Trouver l’identifiant de l’article avec la méthode POST /search PAGEREF _Toc209017050 \h 9

6.2.Étape 2 : Récupérer le contenu de l’article avec la méthode POST /consult/getArticle PAGEREF _Toc209017051 \h 10

7.Recherche simple sur un mot dans un code PAGEREF _Toc209017052 \h 10

7.1.Exemple de requête par état juridique dans le fonds CODE PAGEREF _Toc209017053 \h 10

7.2.Exemple de requête par date de version ans le fonds CODE PAGEREF _Toc209017054 \h 11

8.Recherche d’une expression dans un code PAGEREF _Toc209017055 \h 12

9.Recherche croisée de mots dans les textes consolidés PAGEREF _Toc209017056 \h 13

10.Recherche dans la jurisprudence administrative PAGEREF _Toc209017057 \h 13

11.Recherche dans la jurisprudence judiciaire PAGEREF _Toc209017058 \h 14

11.1.Pour chercher tous les arrêts du mois de janvier 2025 PAGEREF _Toc209017059 \h 14

11.2.Pour chercher par numéro d’affaire PAGEREF _Toc209017060 \h 15

12.Recherche dans les Journaux officiels PAGEREF _Toc209017061 \h 15

13.Recherche dans les conventions collectives PAGEREF _Toc209017062 \h 16

14.Récupération de contenu en masse PAGEREF _Toc209017063 \h 17

Historique des révisions

Version

Date

Auteur

Modifications

V1

27/11/2019

DILA

Initialisation du document

V2

26/07/2021

DILA

Mise à jour du document

V3

17/09/2025

DILA

Mise à jour du document

Connexion OAuth

L’obtention d’un jeton OAuth par une application se fait via le protocole OAuth2.0 avec le flux Client Credentials (https://tools.ietf.org/html/rfc6749#section-4.4).

Des exemples supplémentaires de connexion OAuth (Python, Java, JavaScript) sont disponibles sur le Gitlab de PISTE, après inscription à Gitlab.

Obtention d’un jeton OAuth2.0 avec PISTE

La requête à effectuer est la suivante :

POST https://sandbox-oauth.piste.gouv.fr/api/oauth/token HTTP/1.1

Accept-Encoding: gzip,deflate

Content-Type: application/x-www-form-urlencoded

Content-Length: 140

Host: sandbox-oauth.piste.gouv.fr

Connection: Keep-Alive

User-Agent: Apache-HttpClient/4.1.1 (java 1.5)

grant_type=client_credentials&client_id=<client_id_généré_sur_le_portail>&client_secret=<client_secret_généré_sur_le_portail>&scope=openid

 

La réponse obtenue est la suivante :

{

   "access_token": "th2uv3lq9zY2vAoth59QpYtCSID1iWn0AG6XhnjgAP54eoY1440vp3",

   "token_type": "Bearer",

   "expires_in": 3600,

   "scope": "openid"

}

 

La propriété "access_token" contient le jeton qui doit être envoyé à chaque requête API.

La propriété "expires_in" correspond au délai d’expiration du jeton en seconde.

Consommer l’API

Pour consommer l’API, il suffit d’ajouter l’entête 'Authorization: Bearer <access_token>' à chaque requête.

Par exemple : 

curl -is -H 'Authorization: Bearer ojECscMjYOh215MN6dUvAI3SOmhOa0nbg5R4tYvDWhZu5HB5ejMG74' -X GET https://sandbox-api.piste.gouv.fr/dila/legifrance/lf-engine-app/list/ping'

Pour les requêtes de type POST, il faut ajouter également les entêtes

‘accept: application/json’ et ‘Content-Type: application/json’.

Récupérer un article en vigueur à une date donnée, d'un code dont on connaît l'id

Exemple :

article L. 36-11 au 1er janvier 2018 du code LEGITEXT000006070987 (postes et des communications électroniques)

Étape 1 : Récupérer l’identifiant de l’article avec la méthode POST /search

{

    "recherche": {

        "champs": [

            {

                "typeChamp": "NUM_ARTICLE",

                "criteres": [

                    {

                        "typeRecherche": "EXACTE",

                        "valeur": "L36-11",

                        "operateur": "ET"

                    }

                ],

                "operateur": "ET"

            }

        ],

        "filtres": [

            {

                "facette": "NOM_CODE",

                "valeurs": [

                    "Code des postes et des communications électroniques"

                ]

            },

            {

                "facette": "DATE_VERSION",

                "singleDate": 1514802418000

            }

        ],

        "pageNumber": 1,

        "pageSize": 10,

        "operateur": "ET",

    "sort": "PERTINENCE",

        "typePagination": "ARTICLE"

    },

   "fond": "CODE_DATE"

}

Étape 2 : Récupérer le contenu de l’article avec la méthode POST /consult/getArticle

{

  "id": "LEGIARTI000033219357"

}

Récupérer un article en vigueur à une date donnée, d'un texte numéroté

Exemples : 

l’article 6 nonies au 1er janvier 2018 de l’ordonnance n°58-1100.

l’article 3-1 au 1er janvier 2018 de la loi n° 86-1067

Étape 1 : Trouver l’ordonnance avec la méthode POST /search

{

    "recherche": {

        "champs": [

            {

                "typeChamp": "NUM",

                "criteres": [

                    {

                        "typeRecherche": "EXACTE",

                        "valeur": "58-1100",

                        "operateur": "ET"

                    }

                ],

                "operateur": "ET"

            }

        ],

       "filtres": [

            {

                "facette": "DATE_VERSION",

                "singleDate": 1514802418000

            }

        ],

        "pageNumber": 1,

        "pageSize": 10,

        "operateur": "ET",

    "sort": "PERTINENCE",

        "typePagination": "DEFAUT"

    },

   "fond": "LODA_DATE"

}

Étape 2 : trouver l’article de l’ordonnance avec la méthode POST /search

{

    "recherche": {

        "champs": [

            {

                "typeChamp": "NUM",

                "criteres": [

                    {

                        "typeRecherche": "EXACTE",

                        "valeur": "58-1100",

                        "operateur": "ET"

                    }

                ],

                "operateur": "ET"

            },

            {

                "typeChamp": "NUM_ARTICLE",

                "criteres": [

                    {

                        "typeRecherche": "EXACTE",

                        "valeur": "6 nonies",

                        "operateur": "ET"

                    }

                ],

                "operateur": "ET"

            }

        ],

       "filtres": [

            {

                "facette": "DATE_VERSION",

                "singleDate": 1514802418000

            }

        ],

        "pageNumber": 1,

        "pageSize": 10,

        "operateur": "ET",

    "sort": "PERTINENCE",

        "typePagination": "DEFAUT"

    },

   "fond": "LODA_DATE"

}

Étape 3 : Récupérer le contenu de l’article avec la méthode POST /consult/getArticle

{

  "id": "LEGIARTI000035937614"

}

Récupérer le texte complet d'une loi promulguée dont on connaît le n°

Exemple : 

la loi n°2019-290 en vigueur à la date d'aujourd'hui

Étape 1 : Trouver l’identifiant de la loi avec la méthode POST /search

{

    "recherche": {

        "champs": [

            {

                "typeChamp": "NUM",

                "criteres": [

                    {

                        "typeRecherche": "EXACTE",

                        "valeur": "2019-290",

                        "operateur": "ET"

                    }

                ],

                "operateur": "ET"

            }

        ],

       "filtres": [

            {

                "facette": "DATE_VERSION",

                "singleDate": 1561132975000

            },

            {

                "facette": "TEXT_LEGAL_STATUS",

                "valeur": "VIGUEUR"

            }

        ],

        "pageNumber": 1,

        "pageSize": 10,

        "operateur": "ET",

    "sort": "PERTINENCE",

        "typePagination": "DEFAUT"

    },

   "fond": "LODA_ETAT"

}

Étape 2 : Récupérer le contenu de la loi avec la méthode POST /consult/legiPart

{

  "date": 1561132975000,

  "textId": "LEGITEXT000038359719"

}

Récupérer un article en vigueur à une date donnée, d'une loi identifiée par sa date de signature

Exemples : 

article 57 de la loi du 17 juillet 1978 en vigueur aujourd'hui

Étape 1 : Trouver l’identifiant de la loi avec la méthode POST /search

{

    "recherche": {

        "champs": [

            {

                "typeChamp": "NUM_ARTICLE",

                "criteres": [

                    {

                        "typeRecherche": "EXACTE",

                        "valeur": "57",

                        "operateur": "ET"

                    }

                ],

                "operateur": "ET"

            }

        ],

       "filtres": [

            {

                "facette": "DATE_SIGNATURE",

                "dates":

                    {

                        "start": "1978-07-17",

                        "end": "1978-07-17"

                    }

            },

                    {

                      "facette": "DATE_VERSION",

                      "singleDate": 1571664723166

                    },

                    {

                      "facette": "TEXT_LEGAL_STATUS",

                      "valeur": "VIGUEUR"

                    }

                ],

        "pageNumber": 1,

        "pageSize": 1,

        "operateur": "ET",

        "sort": "PERTINENCE",

        "typePagination": "ARTICLE"

    },

   "fond": "LODA_DATE"

}

Étape2 : Une fois l’identifiant LEGIARTI récupéré, on l’utilise avec la méthode /consult/getArticle

{

  "id": "LEGIARTI000006528277"

}

Récupérer un article en vigueur à une date donnée de la Constitution ou à défaut le texte complet de la Constitution

Exemple :

article 54 de la Constitution

Étape 1 : Trouver l’identifiant de l’article avec la méthode POST /search

{

    "recherche": {

        "champs": [

            {

                "typeChamp": "TITLE",

                "criteres": [

                    {

                        "typeRecherche": "EXACTE",

                        "valeur": "Constitution",

                        "operateur": "ET"

                    }

                ],

                "operateur": "ET"

            },

{

                "typeChamp": "NUM_ARTICLE",

                "criteres": [

                    {

                        "typeRecherche": "EXACTE",

                        "valeur": "54",

                        "operateur": "ET"

                    }

                ],

                "operateur": "ET"

            }

        ],

       "filtres": [

       

            {

                "facette": "DATE_VERSION",

                "singleDate": 1561132975000

            },

            {

                "facette": "TEXT_LEGAL_STATUS",

                "valeur": "VIGUEUR"

            }

        ],

        "pageNumber": 1,

        "pageSize": 10,

        "operateur": "ET",

    "sort": "PERTINENCE",

        "typePagination": "DEFAUT"

    },

   "fond": "LODA_ETAT"

}

Étape 2 : Récupérer le contenu de l’article avec la méthode POST /consult/getArticle

{

  "id": "LEGIARTI000006527539"

}

Recherche simple sur un mot dans un code

Pour rechercher dans les codes, vous avez deux fonds disponibles selon les besoins :

- CODE_ETAT : recherche dans les codes par état juridique

- CODE_DATE : recherche dans les codes par date de version

Exemple de requête par état juridique dans le fonds CODE

{

    "fond": "CODE_ETAT",

    "recherche": {

        "champs": [{

                "typeChamp": "ARTICLE",

                "criteres": [{

                        "typeRecherche": "UN_DES_MOTS",

                        "valeur": "responsabilite",

                        "operateur": "ET"

                    }

                ],

                "operateur": "ET"

            }

        ],

        "filtres": [{

                "facette": "TEXT_NOM_CODE",

                "valeurs": [

                    "Code civil"

                ]

            }

        ],

        "pageNumber": 1,

        "pageSize": 10,

        "operateur": "ET",

        "sort": "PERTINENCE",

        "typePagination": "DEFAUT"

    }

}

Exemple de requête par date de version ans le fonds CODE

{

"fond": "CODE_DATE",

"recherche": {

"champs": [

{

"typeChamp": "ARTICLE",

"criteres": [

{

"typeRecherche": "UN_DES_MOTS",

"valeur": "responsabilite",

"operateur": "ET"

}

],

"operateur": "ET"

}

],

"filtres": [

{

"facette": "NOM_CODE",

"valeurs": [

"Code civil"

]

},

{

"facette": "DATE_VERSION",

"singleDate": "2025-04-15"

}

],

"pageNumber": 1,

"pageSize": 10,

"operateur": "ET",

"sort": "PERTINENCE",

"typePagination": "DEFAUT"

}

}

Recherche d’une expression dans un code

La documentation Swagger précise les valeurs possibles pour "typeRecherche" : 

[ UN_DES_MOTS, EXACTE, TOUS_LES_MOTS_DANS_UN_CHAMP, AUCUN_DES_MOTS, AUCUNE_CORRESPONDANCE_A_CETTE_EXPRESSION ]

Si vous recherchez une expression, vous pouvez indiquer "UN_DES_MOTS" et préciser la proximité, c'est-à-dire la distance maximale, en mots, entre les termes recherchés.

Vous pouvez également sélectionner le type de recherche EXACTE.

Voici un exemple de requête complète par état juridique dans le fonds CODE :

{

    "fond": "CODE_ETAT",

    "recherche": {

        "champs": [{

                "typeChamp": "ARTICLE",

                "criteres": [{

                        "typeRecherche": "UN_DES_MOTS",

                        "valeur": "outrage a agent",

                        "operateur": "ET"

                    }

                ],

                "operateur": "ET"

            }

        ],

        "filtres": [{

                "facette": "TEXT_NOM_CODE",

                "valeurs": [

                    "Code pénal"

                ]

            }

        ],

        "pageNumber": 1,

        "pageSize": 10,

        "operateur": "ET",

        "sort": "PERTINENCE",

        "typePagination": "DEFAUT"

    }

}

Recherche croisée de mots dans les textes consolidés

Pour effectuer une recherche croisée, il suffit de définir plusieurs critères de recherche dans votre requête.

Voici un exemple de requête dans le fonds LODA_DATE :

{

    "fond": "LODA_DATE",

    "recherche": {

        "champs": [{

                "criteres": [{

                        "criteres": [{

                                "typeRecherche": "UN_DES_MOTS",

                                "valeur": "mineur",

                                "operateur": "ET"

                            }

                        ],

                        "operateur": "ET",

                        "proximite": 2,

                        "typeRecherche": "UN_DES_MOTS",

                        "valeur": "travail"

                    }

                ],

                "operateur": "ET",

                "typeChamp": "ALL"

            }

        ],

        "fromAdvancedRecherche": false,

        "operateur": "ET",

        "pageNumber": 1,

        "pageSize": 10,

        "secondSort": "ID",

        "sort": "SIGNATURE_DATE_DESC",

        "typePagination": "DEFAUT"

    }

}

Recherche dans la jurisprudence administrative

Pour chercher tous les arrêts de type « CESEDA » sur une période donnée :

{

    "fond": "CETAT",

    "recherche": {

        "champs": [

            {

                "criteres": [

                    {

                        "valeur": "CESEDA",

                        "proximite": 2,

                        "operateur": "ET",

                        "typeRecherche": "UN_DES_MOTS"

                    }

                ],

                "operateur": "ET",

                "typeChamp": "ALL"

            }

        ],

        "filtres": [

            {

                "facette": "DATE_DECISION",

                "dates": {

                    "start": "2000-01-01",

                    "end": "2005-01-01"

                }

            }

        ],

        "fromAdvancedRecherche": false,

        "pageSize": 100,

        "operateur": "ET",

        "typePagination": "DEFAUT",

        "pageNumber": 1,

        "sort": "PERTINENCE",

        "secondSort": "DATE_DESC"

    }

}

Recherche dans la jurisprudence judiciaire

Pour chercher tous les arrêts du mois de janvier 2025

{

    "fond": "JURI",

    "recherche": {

        "champs": [{

                "criteres": [{

                        "operateur": "ET",

                        "proximite": 2,

                        "typeRecherche": "UN_DES_MOTS",

                        "valeur": "*"

                    }

                ],

                "operateur": "ET",

                "typeChamp": "ALL"

            }

        ],

        "filtres": [{

                "facette": "CASSATION_NATURE_DECISION",

                "valeurs": [

                    "ARRET"

                ]

            }, {

                "facette": "DATE_DECISION",

                "dates": {

                    "start": "2025-01-01",

                    "end": "2025-01-31"

                }

            }

        ],

        "fromAdvancedRecherche": false,

        "operateur": "ET",

        "pageNumber": 1,

        "pageSize": 10,

        "secondSort": "DATE_DESC",

        "sort": "PERTINENCE",

        "typePagination": "DEFAUT"

    }

}

Pour chercher par numéro d’affaire

{

  "fond": "JURI",

  "recherche": {

    "champs": [

      {

        "criteres": [

          {

            "operateur": "ET",

            "typeRecherche": "EXACTE",

            "valeur": "17/030701"

          }

        ],

        "operateur": "ET",

        "typeChamp": "NUM_AFFAIRE"

      }

    ],

    "fromAdvancedRecherche": false,

    "operateur": "ET",

    "pageNumber": 1,

    "pageSize": 10,

    "secondSort": "ID",

    "sort": "DATE_DESC",

    "typePagination": "DEFAUT"

  }

}

Recherche dans les Journaux officiels

Pour récupérer le contenu d’un Journal officiel, vous pouvez procéder de la façon suivante :

Etape 1 :

Récupérer le JORFCONT (identifiant du conteneur d’un Journal officiel) d’une publication d’un JO avec le point d’entrée /consult/lastNJo en passant le nombre de JO que vous voulez récupérer :

{

  "nbElement": 5

}

Ce chiffre doit être inférieur à 2500, sinon vous aurez des erreurs

Etape 2 :

Vous pouvez utiliser le point d’entrée /consult/jorfCont pour récupérer les JORFTEXT (identifiant de chaque texte publié au JO) :

{

  "highlightActivated": true,

  "id": "JORFCONT000022470431",

  "pageNumber": 1,

  "pageSize": 10

}

Via ce point d’entrée vous pouvez aussi passer une période pour récupérer tous les JORFCONT pour une période donnée (cf. la documentation de l’API - swagger).

Etape 3 :

Vous pourrez appeler le point d’entrée /consult/jorf avec les JORFTEXT récupérés à l’étape 2. Cela sera plus pertinent que d’utiliser le point d’entrée getJoWithNor car tous les textes n’ont pas de NOR.

{

  "highlightActivated": true,

  "id": "JORFCONT000022470431",

  "pageNumber": 1,

  "pageSize": 10

}

A noter, les JO anciens ne comportent pas de version HTML des textes. Vous ne pourrez donc pas les récupérer via l’API (avant juin 2004).

Recherche dans les conventions collectives

Pour rechercher des mots-clés dans le titre des conventions collectives :

{

   "fond": "KALI",

   "recherche": {

       "champs": [

           {

               "typeChamp": "TITLE",

               "operateur": "ET",

               "criteres": [

                   {

                       "valeur": "santé prévoyance",

                       "typeRecherche": "TOUS_LES_MOTS_DANS_UN_CHAMP",

                       "operateur": "ET"

                   }

               ]

           }

       ],

       "sort": "SIGNATURE_DATE_DESC",

       "fromAdvancedRecherche": "False",

       "pageNumber": 1,

       "pageSize": 25,

       "typePagination": "DEFAUT",

       "secondSort": "PERTINENCE",

       "operateur": "ET"

   }

}

Pour recherche sur le numéro IDCC :

{

   "fond": "KALI",

   "recherche": {

       "champs": [

           {

               "typeChamp": "IDCC",

               "operateur": "ET",

               "criteres": [

                   {

                       "valeur": "2098",

                       "typeRecherche": "TOUS_LES_MOTS_DANS_UN_CHAMP",

                       "operateur": "ET"

                   }

               ]

           }

       ],

       "sort": "PERTINENCE",

       "fromAdvancedRecherche": "False",

       "pageNumber": 1,

       "pageSize": 25,

       "typePagination": "DEFAUT",

       "operateur": "ET"

   }

}

Récupération de contenu en masse

Alternativement à l’API, vous pouvez aussi utiliser l’open data de Légifrance qui est proposé ici avec toutes nos ressources au format XML :

https://echanges.dila.gouv.fr/OPENDATA/

Les différents freemium de chaque fonds permettent de récupérer l’état du fonds à la date indiquée. Il faut ensuite récupérer les archives suivantes dans l’ordre de la plus ancienne à la plus récente.

Les fonds de Légifrance sont : ACCO / BOCC / CAPP / CASS / CIRCULAIRES / CNIL / CONSTIT / DOLE / Debats  / INCA / JADE / KALI / LEGI / Questions-Reponses.

Vous aurez à chaque fois un document appelé « présentation » expliquant les données que vous pouvez trouver sous chaque fonds. La DTD_LEGIFRANCE vous permettra également de mieux comprendre la structuration des données.