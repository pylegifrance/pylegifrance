Lexique 

Il s’agit d’un document de vulgarisation à destination des réutilisateurs de l’API Légifrance. Celui-ci peut comporter des simplifications. 

 

Actions 

On parle d’action d’un article source d’un texte modificateur vers une ou plusieurs cibles. Ces actions sont de l’ordre de l’insertion/création d’articles ou de niveaux de sections avec les articles associés, l’ajout d’éléments textuels (mots, alinéa...) au niveau de l’article, la modification, la suppression, la renumérotation/transfert d’articles et de sections, le rétablissement d’articles... 

 

Alinéa 

Un article peut comporter plusieurs alinéas. 

Constitue un alinéa toute phrase, tout mot, tout ensemble de phrases ou de mots commençant à la ligne, précédés ou non d’un tiret, d’un point, d’une numérotation ou de guillemets, sans qu’il y ait lieu d’établir des distinctions selon la nature du signe placé à la fin de la ligne précédente (point, deux-points ou point-virgule). Un tableau constitue un seul alinéa (définition complète dans le guide de légistique). 

 

Arrêté 

C’est un acte général, collectif ou individuel émanant d’une autorité administrative : ministre, préfet, maire. 

 

Article 

L’article se définit comme la plus petite partie d’un texte de loi ou d’un règlement administratif qui, pour sa compréhension, se suffit à elle-même. L’article est désigné comme l’unité documentaire. 

L’objet xml d’un article du fonds JORF porte un identifiant de type JORFARTI complété par 12 chiffres. C’est un objet enfant d’un JORFTEXT ou d’un JORFSCTA.  

L’objet xml d’un article dans LEGI porte un identifiant de type LEGIARTI complété par 12 chiffres. C’est un objet enfant d’un LEGITEXT ou d’un LEGISCTA. 

 

CID (Common identifier) 

Le CID est l’identifiant commun à l’ensemble des versions d’un objet xml (article, section, texte). 

De façon générale et sauf erreur dans les données, dans le fonds LEGI, pour les textes non codifiés : 

Le LEGITEXT a comme CID l’identifiant de la version initiale du texte correspondant dans JORF 

Le LEGISCTA a comme CID l’identifiant de la version initiale de la section correspondante dans JORF 

Le LEGIARTI a comme CID l’identifiant de la version initiale de l’article correspondant dans JORF 

Si par exemple un article est créé postérieurement à sa version initiale (JORFTARTI), le CID sera un LEGIARTI. 

 

Pour les codes, le <CID> est un LEGITEXT (puisqu’un code est créé directement dans le fonds LEGI). 

Le LEGITEXT a comme CID l’identifiant de la première version du LEGITEXT 

Le LEGISCTA a comme CID l’identifiant de la première version du LEGISCTA 

Le LEGIARTI a comme CID l’identifiant de la première version du LEGIARTI 

 

Consolidation 

Le principe de consolidation des textes consiste, lorsqu’un article de texte législatif, réglementaire ou conventionnel (ou partie d’un texte ou d’article) est modifié, à le réécrire en y intégrant cette modification. Toute modification, même minime, génère la création d’une version supplémentaire. 

 

Décret 

C’est un acte ou texte administratif de portée générale ou individuelle, signé par le Président de la République ou par le Premier ministre et, parfois, contresigné par un ou plusieurs ministres. C’est une décision qui émane du pouvoir exécutif. 

 

Décret d’application 

C’est un décret qui précise les modalités ou conditions d’application d’une loi (voir guide de légistique). 

 

Décret-loi 

Acte du Gouvernement pris dans un domaine qui relève en principe du pouvoir législatif. Sous la Ve République, le décret-loi qui existait sous les précédentes républiques a été remplacé par l’ordonnance. 

 

Disposition « balai » 

En consolidation, les dispositions « balai » consistent au remplacement d’une ou plusieurs expressions (mots, phrases, acronymes…) présentes dans l’ensemble des dispositions législatives et réglementaires en vigueur (lois, codes, décrets, arrêtés) par une ou plusieurs autres expressions. 

Exemple : article 19 du décret n° 2019-1360 du 13 décembre 2019 : « Dans tous les actes individuels et réglementaires en vigueur qui les mentionnent, les mots : « Institut français des sciences et technologies des transports, de l'aménagement et des réseaux » ou « université de Marne-la-Vallée » sont remplacés par les mots : « Université Gustave Eiffel ». 

 

Etats juridiques d’un article (exemple dans un code) 

Vigueur (abréviation : V) : cas d’un article qui s’applique à la date courante. 

 

Vigueur avec terme (abréviation : VT) désigné également par abrogé différé : cas d’un article en vigueur à la date courante, mais sa fin de vigueur est déjà prévue à une date connue et précisée, il passera à son nouveau statut (modifié ou abrogé). 

 

Vigueur différée (abréviation : VD) : cas d’un article qui entre en vigueur à une date ultérieure. Lorsque cette date est connue, cet état de vigueur différée est renseigné. 

 

Abrogé (abréviation : Ab) : cas d’un article qui n’est plus en vigueur par suite d’une abrogation explicite par un texte publié au Journal officiel. 

 

Annulé (abréviation : A) : cas d’un article de code annulé par décision du Conseil d’État à la suite d’un recours. 

 

Disjoint (abréviation : D) : cas d’un article « séparé » du code ; ses dispositions ne sont plus appliquées. Cette disjonction peut ne pas être définitive ; ses dispositions peuvent être rétablies par un nouveau texte. Cet état juridique est spécifique à la législation fiscale. 

 

Modifié (abréviation : M) : cas d’un article faisant l’objet d’une modification, ponctuation, remplacement ou suppression d’un mot, groupe de mots ou de tout le contenu qui entraîne la création d’une version dite « modifiée ». 

 

Modifié mort-né (abréviation : MMN) : cas d’un article modifié ou abrogé avant la date fixée pour son entrée en vigueur, considéré comme n’ayant jamais eu d’existence légale. 

 

Périmé (abréviation : P) : cas d’un article faisant l’objet d’une abrogation implicite ; c’est le cas, par exemple, de l’article 39 octies du code général des impôts. 

 

Transféré (abréviation : T) : cas d’un article dont les dispositions sont reprises sous un autre numéro d’article. Exemple : l’article L. 821-5-2 du code de commerce est devenu l’article L. 821-5-3 du même code. 

 

Guide de légistique 

Le guide de légistique a pour objet de présenter l’ensemble des règles, principes et méthodes qui doivent être observés dans la préparation des textes normatifs : lois, ordonnances, décrets, arrêtés. La troisième édition mise à jour en 2017 est disponible sur Légifrance : 

https://www.legifrance.gouv.fr/contenu/Media/Files/autour-de-la-loi/guide-de-legistique/guide-de-legistique-edition-2017-format-pdf.pdf 

https://www.legifrance.gouv.fr/contenu/Media/Files/autour-de-la-loi/guide-de-legistique/guide-de-legistique-edition-2017-format-e-pub.epub 

 

Informations nominatives à accès protégé (INAP) 

Les textes INAP sont uniquement présents dans le fonds JORF et n’ont pas vocation à être consolidés. Les « informations nominatives à accès protégé » (INAP)‎ sont limitativement énumérées aux articles R 221-15 et R 221-16 du code des relations entre le public et l'administration pris en application de l'article L. 221-14 après avis de la commission nationale de l'informatique et des libertés (CNIL). 

 

JORF : Journal officiel de la République française 

 

Journal Officiel (un) 

Publication officielle qui assure l’information des citoyens sur les actes législatifs et réglementaires à portée générale. Le JORF existe dans une version électronique authentifiée (JOEA) depuis juin 2004. 

Un Journal officiel est composé d’un ou plusieurs textes à une date de publication. Dans des cas d’exception il peut y avoir plusieurs JO à la même date de publication (JORF n°0001 du 1er janvier 2021 et JORF n°0002 du 1 er janvier 2021).  

L’objet xml d’un Journal Officiel porte un identifiant de type JORFCONT complété par 12 chiffres. Il est parent d’un ou plusieurs JORFTEXT. 

 

LEGI (ou base LEGI) :  

Le texte intégral consolidé de la législation et de la réglementation nationale. Il est essentiellement constitué par : 

les codes officiels ; 

les lois (textes non codifiés), 

les décrets-lois, ordonnances, décrets et une sélection d’arrêtés (textes non codifiés). 

 

Loi 

Règle de droit écrite, de portée générale et impersonnelle (article 34 de la Constitution). Elle s’applique à tous sans exception et nul ne peut se prévaloir de son ignorance. Elle est délibérée, rédigée, amendée et votée par le Parlement (Assemblée nationale et Sénat) en termes identiques. Elle est promulguée (signée) par le Président de la République et publiée au Journal officiel de la République française (JORF). 

 

Loi constitutionnelle 

C’est une loi qui modifie la Constitution. 

 

Loi de finances 

C’est une loi qui fixe les recettes et les dépenses de l’État pour une année. 

 

Loi de financement de la sécurité sociale 

C’est une loi qui autorise le budget de la sécurité sociale pour une année. 

 

Loi organique 

C’est une loi qui précise les conditions d’application de la Constitution ; elle structure les institutions. 

 

Nota 

Le nota consiste en l’insertion d’une note d’information n’ayant pas de valeur juridique en elle-même, mais permettant à l’usager d’avoir des informations complémentaires sur une disposition législative ou réglementaire. 

Exemple : entrée en vigueur à diverses dates, diverses entrées en vigueur au sein d’un même article (ex : alinéas ou 1°, 2°…), annulation ou déclaration d’illégalité du Conseil d’Etat impactant le texte en question. 

Le nota peut être au niveau article ou au niveau texte. Pour des raisons de clarté et d’uniformité de la rédaction sur Légifrance, le nota doit impérativement commencer par “Conformément aux dispositions du/des articles du texte...”ou bien « Par décision du… ». 

 

Notice 

Les informations qui figurent en « chapeau » de certains décrets sont communément désignés selon la terminologie comme « notices explicatives ». La rédaction de ces notices incombe au ministère émetteur ou au secrétariat général du Gouvernement lors de la procédure de soumission du texte à sa signature. La notice lorsqu’elle existe est placée avant les visas. Elle n’a pas de valeur légale. La notice constitue une « aide à la lecture » lorsque le texte juridique présente un caractère peu familier pour son destinataire. 

 

NOR 

Numéro d’identification unique depuis 1987 issu du système normalisé NOR attribué aux actes publiés au Journal officiel et à tous les textes de portée générale publiés dans les Bulletins officiels des ministères. 

Ce NOR est composé de douze caractères alphanumériques : 

un code de trois lettres identifie le ministère ou le secrétariat d’État, selon une table de codification interministérielle gérée par le secrétariat général du Gouvernement ; 

une lettre identifie la direction ou le service intéressé par le texte, selon une liste codée ; 

deux chiffres identifient l’année d’initiation du texte ; 

cinq chiffres identifient le numéro d’ordre du texte dans une séquence de chiffres propre à chaque auteur institutionnel ; 

une lettre identifie la nature du texte. 

 

Ordonnance 

C’est un acte émis par le Gouvernement dans un domaine qui relève en principe de la loi (art. 38 de la Constitution de 1958). Avant sa ratification, l’ordonnance est de nature réglementaire, après ratification elle prend une nature législative. 

 

Section 

Une section est un objet JORFSCTA dans le fonds JORF ou LEGISCTA dans le fonds LEGI (SCTA : Section Texte Article). 

Une section correspond à un niveau de tables des matières.  

L’objet xml d’une section du JO porte un identifiant de type JORFSCTA complété par 12 chiffres. C’est un objet enfant d’un JORFTEXT ou d’un JORFSCTA.  

L’objet xml d’une section dans un texte LEGI porte un identifiant de type LEGISCTA complété par 12 chiffres. C’est un objet enfant d’un LEGITEXT ou d’un LEGISCTA. A titre d’exemple un code peut comporter les niveaux de tables des matières suivantes : 

Partie 

Livre 

Titre 

Sous-titre 

Chapitre 

Section 

Sous-section 

 

Statut d’un article 

Le statut d’un article correspond au champ « type » pour les articles dans le fonds LEGI. La notion existe uniquement au niveau de l’article. Le statut d’un article, pour une version donnée (identifiant LEGIARTI), est soit “entièrement modificateur”, “partiellement modificateur” ou “autonome”. 

 

Statut d’un article de type entièrement modificateur 

Le contenu de l'article dans son intégralité est uniquement porteur d'actions impactant une ou plusieurs cibles. Il est donc qualifié de « entièrement modificateur ». Il ne sera pas, par définition, une cible d’un autre texte modificateur. En conséquence un article entièrement modificateur n’a pas d’état juridique (ni de date de début de vigueur, ni de date de fin de vigueur).    

  

Statut d’un article de type partiellement modificateur 

Une partie du contenu de l’article est porteur d’actions sur une ou plusieurs cibles et une autre partie du contenu est sans action. Il est donc qualifié d’article partiellement modificateur. 

Cet article pourra être lui-même la cible d’un texte modificateur issu d’un JO publié ultérieurement, mais uniquement dans la partie du contenu non modificateur.  

La partie modificatrice de l’article ne pourra pas être la cible d’un autre texte modificateur.  

En conséquence, un article partiellement modificateur a un état juridique, une date de début de vigueur et potentiellement une date de fin de vigueur.  

  

Statut d’un article de type autonome  

Le contenu de l'article dans son intégralité n’engendre aucune action par rapport à une ou plusieurs cibles. Il est donc qualifié d’autonome. Il pourra être ensuite lui-même la cible d’un texte modificateur issu d’un JO publié ultérieurement. En conséquence un article autonome a un état juridique, une date de début de vigueur. 

 

Texte 

Un texte peut être désigné comme un ensemble d’article(s) contenant ou non des sections. Un texte publié au Journal officiel est désigné également comme la “version initiale”.  

L’objet xml d’un texte dans le fonds JORF porte un identifiant de type JORFTEXT complété par 12 chiffres. C’est un objet enfant d’un JORFCONT (sommaire JO). 

L’objet xml d’un texte dans le fonds LEGI porte un identifiant de type LEGITEXT complété par 12 chiffres. 

 

Texte cible 

Texte sur lequel vont être faites les modifications. 

 

Texte modificateur 

Texte comprenant les demandes de modifications à faire sur d’autres textes. C’est le texte “source de la modification”. 

 

Version dans LEGI 

La version d’un texte, d’une section ou d’un article dans le fonds LEGI est notamment caractérisée par un identifiant (id LEGITEXT, id LEGISCTA, id LEGIARTI), un contenu, un état juridique, une date de début de vigueur et une date de fin de vigueur. Si un article dans LEGI possède plusieurs versions on parle communément de pile de versions.  

Si une version d’article est “modifiée” par une source, l’article cible est “versionné” c’est à dire qu’une nouvelle version de l’article est créée. 

Dans le cas d’un article dont le statut est entièrement modificateur, la version de l’article n’a pas d’état juridique, de date de début de vigueur ni date de fin de vigueur. 

 

A quoi correspondent les lettres L, R, D, A placées devant un numéro d’article de code ? 

La lettre traduit la partie du code à laquelle l’article est rattaché : 

L : partie législative (LO – loi organique) ; 

R : partie réglementaire – décret pris en Conseil d’État ; 

D : partie réglementaire – décret simple ; 

A : partie arrêtés. 

 

A quoi correspondent les astérisques * ou ** situés à côté d’un article de code ? (Ne pas confondre cet astérisque avec celui utilisé comme troncature) 

Les R* sont les articles issus d’un décret en Conseil d’Etat pris en conseil des ministres et les R sont les articles issus d’un décret en Conseil d’État. 

Les D* sont les articles issus d’un décret simple pris en conseil des ministres et les D sont les articles issus d’un décret simple. 

 

Quelle est la différence entre un texte législatif et un texte réglementaire ? 

Un texte législatif est issu du Parlement donc voté par les deux assemblées parlementaires (Assemblée nationale et Sénat). 

Un texte réglementaire est issu du Gouvernement, il est rédigé selon les règles de légistique par un département ministériel sous la responsabilité de son ministre et/ou du Premier ministre.