# Test technique Python — Calcul de panier avec remises

Fonction `calculate_total(cart, rules)` qui calcule le total d'un panier en appliquant :

1. **Une remise au volume par article** : si la quantité d'un article atteint un seuil de `rules["volume_discounts"]`, son prix unitaire est réduit (le plus gros seuil atteint l'emporte).
2. **Une offre "3 pour 2" par catégorie** : pour les catégories de `rules["bundle_categories"]`, dans chaque tranche de 3 articles (tous produits de la catégorie confondus), le moins cher est offert.

La remise volume est appliquée avant l'offre groupée, et le total est arrondi à 2 décimales.

## Lancer le code

```bash
python calculate_total.py
```

## Lancer les tests

```bash
pip install -r requirements-dev.txt
pytest
```

## Choix d'implémentation

- **Dépliage des quantités** : pour l'offre groupée, chaque unité est traitée séparément (4 × A + 1 × B devient une liste de 5 prix), puisque la règle mélange tous les produits d'une même catégorie.
- **Formation des groupes** : l'énoncé ne précise pas comment former les tranches de 3. J'ai trié les prix par ordre décroissant puis découpé en groupes de 3, ce qui fait que le 3e élément de chaque groupe est automatiquement le moins cher. C'est la convention la plus courante pour ce type d'offre.
- **Règles absentes** : si `volume_discounts` ou `bundle_categories` manque, la règle correspondante est simplement ignorée.

## Limites et pistes d'amélioration

- Les prix sont manipulés en `float`. En production, j'utiliserais `decimal.Decimal` pour éviter les erreurs d'arrondi sur des montants.
- Le dépliage des quantités donne une complexité en O(n log n) sur le nombre total d'unités. Pour de très grosses quantités, on pourrait regrouper par prix au lieu de créer une entrée par unité.
- La taille du pack (3) est en dur ; elle pourrait devenir un paramètre de `rules` pour gérer d'autres offres (4 pour 3, etc.).
