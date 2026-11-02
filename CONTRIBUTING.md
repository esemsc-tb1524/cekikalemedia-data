# Contribuer

Merci ! Ces données sont publiques et concernent des entreprises et des personnes réelles : la rigueur compte plus que la quantité.

## La règle d'or : une source publique par affirmation

Une fiche sans `source_url` est refusée. Sources acceptées :
- documents officiels : rapport annuel, document d'enregistrement universel, registre du commerce, décisions de l'Arcom ou de l'Autorité de la concurrence, Journal officiel ;
- mentions légales ou page « qui sommes-nous » du média ou de son propriétaire ;
- presse reconnue, en privilégiant la plus récente.

Non acceptés : rumeurs, réseaux sociaux, forums, affirmations sans lien, opinions sur la ligne éditoriale. La base dit **qui possède**, pas ce qu'il faut en penser.

## Option 1 : sans Git

Ouvrez une [issue](../../issues/new/choose) :
- **Ajouter un média** : domaine, propriétaire, sources ;
- **Signaler une erreur ou un changement** : domaine, ce qui est faux, sources.

Une personne du projet la transforme en modification du fichier.

## Option 2 : pull request

1. Forkez le dépôt et modifiez [`data/media.csv`](data/media.csv).
2. Respectez les colonnes décrites dans le [README](README.md#les-données). Rédigez `information` sur le modèle des lignes existantes, par exemple `Famille Dassault (Groupe Figaro / CCM Benchmark)`.
3. Vérifiez en local :
   ```sh
   python3 scripts/validate.py --fix   # remet le fichier en forme (tri, fins de ligne)
   python3 scripts/validate.py
   ```
4. Ouvrez la *pull request* en remplissant le modèle. La vérification automatique doit être verte.

### Conseils

- **Cession en cours ou propriétaire incertain** : dites-le dans `information`, avec la date, par exemple `… ; cession à X annoncée, non finalisée au 11/10/2026`. N'écrivez pas ce qui n'est pas établi.
- **Média disparu ou domaine abandonné** : mettez `active` à `FALSE` plutôt que de supprimer la ligne.
- **Plusieurs sources** : séparez-les par ` | ` (espace, barre verticale, espace).
- **Un seul sujet par pull request** : c'est plus rapide à relire.

## Relecture

Chaque changement est relu par un mainteneur avant fusion : le format est vérifié automatiquement, les sources sont vérifiées à la main. Il peut vous demander une source supplémentaire. Les délais dépendent de la disponibilité des mainteneurs.

## Licence de vos contributions

En contribuant, vous acceptez que votre contribution soit publiée sous la licence des données du dépôt ([LICENSE-DATA.md](LICENSE-DATA.md)), et sous la licence MIT pour le code. Ne copiez pas de contenu protégé : les faits (qui possède quoi) sont libres, pas les articles ni les bases d'autres éditeurs.

## Conduite

Restez factuel et courtois. Les commentaires visant des personnes plutôt que des données seront supprimés.
