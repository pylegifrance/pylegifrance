# Recherche dans les codes

Pour la liste des codes disponibles : [https://www.legifrance.gouv.fr/liste/code?etatTexte=VIGUEUR](https://www.legifrance.gouv.fr/liste/code?etatTexte=VIGUEUR)

```python
from pylegifrance import LegifranceClient
from pylegifrance.fonds.code import Code
from pylegifrance.models.code.enum import NomCode

# Initialiser le client et l'interface Code
client = LegifranceClient(client_id="...", client_secret="...")
code = Code(client)

# Obtenir l'article 7 du Code civil
resultats = (code.search()
                .in_code(NomCode.CC)  # Code civil
                .article_number("7")
                .execute())

# Obtenir l'article 7 du Code civil avec formatage
resultats = (code.search()
                .in_code(NomCode.CC)  # Code civil
                .article_number("7")
                .with_formatter()
                .execute())

# Obtenir l'intégralité du Code civil
resultats = (code.search()
                .in_code(NomCode.CC)  # Code civil
                .execute())

# Rechercher le mot "sûreté" dans les articles du Code civil
resultats = (code.search()
                .in_code(NomCode.CC)  # Code civil
                .text("sûreté")
                .execute())
```

La classe `Code` permet la recherche dans les codes juridiques français (CODE_DATE, CODE_ETAT) d'un article par son numéro, d'un terme de recherche ou d'un code dans son intégralité, en utilisant une API fluide.

Par défaut, la recherche s'effectue sur les codes en vigueur à la date actuelle. 
Pour effectuer une recherche historique, utilisez la méthode `at_date()` ou initialisez avec `fond="CODE_DATE"`.

**! Attention** : Il est de la responsabilité exclusive de l'utilisateur de vérifier que les informations renvoyées par l'API sont pertinentes et à jour.

# Options supplémentaires de recherche

```python
# Formatage des résultats
resultats = (code.search()
                .in_code(NomCode.CC)  # Code civil
                .article_number("7")
                .with_formatter()
                .execute())

# Recherche à une date spécifique
resultats = (code.search()
                .in_code(NomCode.CC)  # Code civil
                .at_date("2020-01-01")
                .execute())

# Pagination des résultats
resultats = (code.search()
                .in_code(NomCode.CC)  # Code civil
                .text("contrat")
                .paginate(page_number=1, page_size=20)
                .execute())
```
