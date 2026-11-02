# Gouvernance

## Qui décide

Pour l'instant, le projet est tenu par son créateur, seul mainteneur. D'autres mainteneurs peuvent être ajoutés ; ils doivent avoir contribué régulièrement et respecté la règle des sources.

- La branche `main` est protégée : aucune modification directe, tout passe par une *pull request* relue.
- Un mainteneur ne fusionne pas ses propres changements sans relecture lorsqu'il y a plusieurs mainteneurs.

## Ce qui est publié

- Une fiche = un nom de domaine, un propriétaire, au moins une source publique.
- Un changement de propriétaire non finalisé est signalé comme tel dans `information`, avec la date de vérification.
- Les fiches ne sont jamais supprimées de la base publiée : elles sont désactivées (`active = FALSE`).

## Corrections et demandes des personnes concernées

Un média, un propriétaire ou toute autre personne concernée peut demander une correction via une [issue](../../issues/new/choose) « Signaler une erreur ». Les règles sont les mêmes pour tout le monde :

1. La demande doit indiquer ce qui est inexact et fournir une source publique.
2. Si la source est convaincante, la fiche est corrigée rapidement, en visant quelques jours.
3. Si l'information est exacte et sourcée, elle est maintenue ; la réponse l'explique.
4. En cas de doute sérieux et de risque de préjudice, la fiche peut être désactivée le temps de la vérification.
5. Pour toute demande ne pouvant être adressée par voie publique, merci de vous adresser à tim.boudot@editions-boudot.com

## Mise en place de la publication

Action réservée à l'administrateur du dépôt.

1. **Supabase** : la table `public.site_information` existe déjà (voir `supabase/setup.sql` dans le dépôt de l'extension). Elle ne doit pas être modifiée à la main ensuite.
2. **Secrets GitHub** (Settings → Secrets and variables → Actions → New repository secret) :
   - `SUPABASE_URL` : l'URL du projet Supabase (`https://xxxx.supabase.co`), **pas** `data.cekikalemedia.fr`, qui est un proxy en lecture seule ;
   - `SUPABASE_SERVICE_ROLE_KEY` : la clé *service_role* du projet. Elle contourne la sécurité par ligne : ne la mettez jamais dans le code, l'extension ou le site.
3. **Protection de `main`** (Settings → Branches → Add rule) : exiger une *pull request*, exiger que le contrôle « Validate data » soit vert, interdire les pushs directs.
4. **Premier essai** : onglet Actions → « Publish to Supabase » → *Run workflow* avec `dry_run` activé. Le journal liste les lignes qui seraient désactivées. Vérifiez, puis relancez sans `dry_run`, ou laissez la prochaine fusion le faire.
5. **Fork et secrets** : GitHub n'expose pas les secrets aux *pull requests* venant de forks, c'est voulu : la publication ne se déclenche qu'après fusion dans `main`.

## Mise à jour automatique du site web

Après chaque publication réussie, le workflow prévient le dépôt du site (`tim-boudot/cekikalemedia_website`), qui régénère ses bulles et son quiz depuis `data/media.csv` à ce commit précis puis se redéploie. Le site se reconstruit aussi seul chaque jour, au cas où une notification serait perdue.

Mise en place (administrateur) :

1. Sur GitHub, créez un **jeton d'accès personnel à portée limitée** (Settings → Developer settings → Personal access tokens → Fine-grained tokens), avec comme propriétaire le compte qui possède le dépôt du site :
   - *Repository access* : uniquement `cekikalemedia_website` ;
   - *Permissions* : **Contents : Read and write** (nécessaire pour envoyer l'événement) ;
   - une date d'expiration (par exemple un an), à renouveler.
2. Dans ce dépôt-ci, ajoutez-le comme secret `WEBSITE_DISPATCH_TOKEN` (Settings → Secrets and variables → Actions).
3. Sans ce secret, tout fonctionne quand même : seule la mise à jour du site attend alors la reconstruction quotidienne.

## Garde-fous de la publication

- Le fichier est validé avant d'être envoyé ; un fichier invalide n'est jamais publié.
- La publication refuse de désactiver plus de la moitié des fiches actives d'un coup (protection contre un fichier tronqué).
- Pour annuler une erreur : revenez au commit précédent (`git revert`) ; la fusion relance la publication.
