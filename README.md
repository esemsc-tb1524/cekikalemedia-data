# cekikalemedia-data

Base de données publique recensant la possession des médias. Elle alimente l'extension Chrome [Cékikalemédia](https://chromewebstore.google.com/detail/cekikalemedia/ndmjfcngaappkehhgbacmficjhefdime) et le site [cekikalemedia.fr](https://cekikalemedia.fr).

**Tout le monde peut contribuer** : ajouter un média, corriger une fiche, signaler un changement de propriétaire. Chaque affirmation doit s'appuyer sur une source publique.

## Les données

Un seul fichier : [`data/media.csv`](data/media.csv), une ligne par nom de domaine.

| Colonne | Contenu |
|---|---|
| `domain` | nom d'hôte en minuscules, sans `https://` ni chemin (`lemonde.fr`) |
| `information` | qui possède le média, tel qu'affiché dans la bannière de l'extension |
| `include_subdomains` | `TRUE` si les sous-domaines (`www.`, `abonnes.`…) sont couverts |
| `active` | `TRUE` pour que la fiche soit publiée ; `FALSE` pour la retirer sans la supprimer |
| `link_url` | lien « pour en savoir plus » (facultatif, https) |
| `source_url` | **obligatoire** : une ou plusieurs sources publiques, `https://…`, séparées par ` | ` |

Le fichier est trié par domaine, en UTF-8, avec des fins de ligne LF. `python3 scripts/validate.py --fix` le remet en forme.

## Comment contribuer

Voir [CONTRIBUTING.md](CONTRIBUTING.md). En bref :
- sans passer par Git : ouvrez une [*issue*](../../issues/new/choose) (« Ajouter un média » ou « Signaler une erreur ») ;
- avec Git : modifiez `data/media.csv` et ouvrez une *pull request*. Une vérification automatique contrôle le format et la présence de sources.

Une relectrice ou un relecteur valide chaque changement avant sa publication ([GOUVERNANCE.md](GOUVERNANCE.md)).

## Publication

```
pull request ──▶ validation automatique ──▶ relecture ──▶ fusion dans main
                                                               │
                                       GitHub Action « Publish to Supabase »
                                                               ▼
                         Supabase (lecture publique) ──▶ data.cekikalemedia.fr ──▶ extension
```

Rien n'est modifié à la main dans Supabase : la base publiée est une copie de ce dépôt. Une fiche retirée du CSV est désactivée (`active = false`), jamais supprimée.

## Développement

Python 3.10+ suffit, sans dépendances.

```sh
python3 scripts/validate.py                    # vérifie data/media.csv
python3 -m unittest discover -s tests -v       # tests du validateur
SUPABASE_URL=… SUPABASE_SERVICE_ROLE_KEY=… python3 scripts/sync_supabase.py --dry-run
```

Mise en place de la publication (administrateur) : voir [GOUVERNANCE.md](GOUVERNANCE.md#mise-en-place-de-la-publication).

## Licences

- **Données** (`data/`) : voir [LICENSE-DATA.md](LICENSE-DATA.md).
- **Code** (`scripts/`, `tests/`, `.github/`) : [MIT](LICENSE).
