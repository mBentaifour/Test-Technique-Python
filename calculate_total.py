def calculate_total(cart: list[dict], rules: dict) -> float:
    """Calcule le total d'un panier après remises volume et offre 3 pour 2."""
    volume_discounts = rules.get("volume_discounts", {})
    bundle_categories = set(rules.get("bundle_categories", []))

    total = 0.0
    # prix unitaires (déjà remisés) des articles éligibles au pack, par catégorie
    bundle_prices = {}

    for item in cart:
        price = item["price"]
        qty = item["qty"]

        # Règle 1 : on prend le plus gros seuil atteint
        discount = 0.0
        for threshold, rate in sorted(volume_discounts.items()):
            if qty >= threshold:
                discount = rate
        unit_price = price * (1 - discount)

        if item["category"] in bundle_categories:
            # on "déplie" la quantité pour traiter chaque unité séparément
            bundle_prices.setdefault(item["category"], []).extend([unit_price] * qty)
        else:
            total += unit_price * qty

    # Règle 2 : 3 pour 2 par catégorie
    for prices in bundle_prices.values():
        # tri décroissant puis groupes de 3 : le 3e de chaque groupe est le moins cher
        prices.sort(reverse=True)
        for i, p in enumerate(prices):
            if i % 3 == 2:
                continue  # offert
            total += p

    return round(total, 2)


if __name__ == "__main__":
    rules = {
        "volume_discounts": {5: 0.10, 10: 0.20},
        "bundle_categories": ["book"],
    }
    cart = [
        {"id": "A", "category": "book", "price": 10.0, "qty": 4},
        {"id": "B", "category": "book", "price": 15.0, "qty": 1},
        {"id": "C", "category": "tech", "price": 100.0, "qty": 1},
    ]
    print("Total :", calculate_total(cart, rules))
