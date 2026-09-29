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

- **Regroupement par article** : les lignes d'un même `id` sont fusionnées avant la remise volume (2 lignes de 3 × A comptent comme 6 × A). Un même `id` avec un prix ou une catégorie différents est refusé.
- **Dépliage des quantités** : pour l'offre groupée, chaque unité est traitée séparément, puisque la règle mélange tous les produits d'une même catégorie.
- **Formation des groupes** : l'énoncé ne précise pas comment former les tranches. Les prix sont triés par ordre décroissant puis découpés en groupes de N ; le dernier de chaque groupe (le moins cher) est offert. Ce découpage maximise la remise accordée au client (ex. 30, 20, 10, 10, 5, 5 → 15 € offerts). Si le métier voulait l'inverse, seul le tri serait à changer.
- **Montants en `Decimal`** : tous les calculs sont faits en `decimal.Decimal` et arrondis au centime avec `ROUND_HALF_UP` (en float, `round(1.005, 2)` donne `1.0`). La fonction renvoie un `float` pour garder la signature de l'énoncé.
- **Taille du pack paramétrable** : `rules["bundle_size"]` (3 par défaut) permet de gérer un « 4 pour 3 », etc.
- **Validation des entrées** : champ manquant, quantité négative ou non entière, prix négatif, taux hors de [0, 1], seuil ≤ 0 ou `bundle_size` < 2 lèvent une `ValueError` / `TypeError` explicite.
- **Règles absentes** : si `volume_discounts` ou `bundle_categories` manque, la règle correspondante est ignorée.

## Limites et pistes d'amélioration

- Le dépliage des quantités est en O(n log n) sur le nombre total d'unités. Pour de très grosses quantités, on pourrait raisonner par paliers de prix au lieu de créer une entrée par unité.
- En production, les montants seraient plutôt stockés en centimes (entiers) ou en `Decimal` de bout en bout, y compris dans la valeur de retour.
- L'ordre d'application des règles (volume puis pack) est fixe ; un moteur de règles permettrait de le configurer.
