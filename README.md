# Last Piece Ltd — V4 (catalogue réel)

Site statique GitHub Pages avec catalogue Star Wars et Harry Potter provenant des exports publics Rebrickable.

## Première installation
1. Décompresser l'archive et ajouter `index.html`, `scripts/update_catalog.py` et `.github/workflows/catalog.yml` à la racine du dépôt GitHub.
2. Dans GitHub > Actions, ouvrir **Mettre à jour le catalogue LEGO**, puis **Run workflow**.
3. Après réussite, vérifier que `data/catalog.json` a été créé. Le site charge automatiquement ce fichier.
4. Vérifier Settings > Actions > General > Workflow permissions : autoriser **Read and write permissions** si la publication échoue sur `git push` (ou régler les permissions appropriées).
5. GitHub Pages doit rester configuré sur `main` / `(root)`.

La mise à jour automatique est programmée chaque lundi. Aucun token API n'est nécessaire pour ces fichiers CSV publics. Le site ne récupère **aucun prix, historique de vente ou prévision réelle** automatiquement : les colonnes financières restent vides tant que des observations vérifiées ne sont pas importées.

Images : URL du visuel principal Rebrickable, selon disponibilité. Ce visuel peut montrer le set construit plutôt que la boîte ; une photo de l'emballage n'est pas garantie. Respecter les conditions de réutilisation des sources.

Les favoris et imports restent dans le navigateur ; ils ne sont pas partagés entre associés.
