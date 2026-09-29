from decimal import ROUND_HALF_UP, Decimal

CENT = Decimal("0.01")
DEFAULT_BUNDLE_SIZE = 3


def _to_decimal(value, field: str) -> Decimal:
    """Convertit un nombre en Decimal sans hériter des imprécisions du float."""
    if isinstance(value, bool) or not isinstance(value, (int, float, Decimal, str)):
        raise TypeError(f"{field} doit être un nombre, reçu {value!r}")
    try:
        return Decimal(str(value))
    except ArithmeticError as exc:
        raise ValueError(f"{field} invalide : {value!r}") from exc


def _merge_cart(cart: list[dict]) -> list[dict]:
    """Regroupe les lignes d'un même article (même id) en additionnant les quantités.

    Sans ce regroupement, 2 lignes de 3 x A ne déclencheraient pas une remise
    volume à partir de 5 unités, alors que le client achète bien 6 x A.
    """
    merged: dict[str, dict] = {}
    for line_no, item in enumerate(cart, start=1):
        for key in ("id", "category", "price", "qty"):
            if key not in item:
                raise ValueError(f"ligne {line_no} : champ '{key}' manquant")

        qty = item["qty"]
        if isinstance(qty, bool) or not isinstance(qty, int):
            raise TypeError(f"ligne {line_no} : qty doit être un entier, reçu {qty!r}")
        if qty < 0:
            raise ValueError(f"ligne {line_no} : qty négative ({qty})")

        price = _to_decimal(item["price"], f"ligne {line_no} : price")
        if price < 0:
            raise ValueError(f"ligne {line_no} : prix négatif ({price})")

        existing = merged.get(item["id"])
        if existing is None:
            merged[item["id"]] = {"category": item["category"], "price": price, "qty": qty}
        else:
            if existing["price"] != price or existing["category"] != item["category"]:
                raise ValueError(
                    f"article '{item['id']}' présent plusieurs fois avec un prix "
                    "ou une catégorie différents"
                )
            existing["qty"] += qty
    return list(merged.values())


def _volume_rate(qty: int, volume_discounts: dict) -> Decimal:
    """Retourne le taux du plus gros seuil atteint (0 si aucun)."""
    rate = Decimal("0")
    best_threshold = 0
    for threshold, threshold_rate in volume_discounts.items():
        if qty >= threshold > best_threshold:
            best_threshold = threshold
            rate = _to_decimal(threshold_rate, "taux de remise")
    return rate


def _validate_rules(rules: dict) -> tuple[dict, set, int]:
    volume_discounts = rules.get("volume_discounts") or {}
    for threshold, rate in volume_discounts.items():
        if isinstance(threshold, bool) or not isinstance(threshold, int) or threshold <= 0:
            raise ValueError(f"seuil de remise invalide : {threshold!r}")
        if not Decimal("0") <= _to_decimal(rate, "taux de remise") <= Decimal("1"):
            raise ValueError(f"taux de remise hors de [0, 1] : {rate!r}")

    bundle_categories = set(rules.get("bundle_categories") or [])

    bundle_size = rules.get("bundle_size", DEFAULT_BUNDLE_SIZE)
    if isinstance(bundle_size, bool) or not isinstance(bundle_size, int) or bundle_size < 2:
        raise ValueError(f"bundle_size doit être un entier >= 2, reçu {bundle_size!r}")

    return volume_discounts, bundle_categories, bundle_size


def calculate_total(cart: list[dict], rules: dict) -> float:
    """Calcule le total d'un panier après remise volume puis offre groupée.

    - Remise volume : par article (lignes de même id regroupées), le plus gros
      seuil atteint l'emporte.
    - Offre groupée ("3 pour 2" par défaut, configurable via rules["bundle_size"]) :
      par catégorie éligible, dans chaque tranche de N unités, la moins chère est offerte.
    - Calculs en Decimal, arrondi final au centime (ROUND_HALF_UP).
    """
    volume_discounts, bundle_categories, bundle_size = _validate_rules(rules or {})

    total = Decimal("0")
    # prix unitaires (déjà remisés) des unités éligibles à l'offre, par catégorie
    bundle_prices: dict[str, list[Decimal]] = {}

    for item in _merge_cart(cart):
        # Règle 1 : remise volume
        unit_price = item["price"] * (1 - _volume_rate(item["qty"], volume_discounts))

        if item["category"] in bundle_categories:
            # on "déplie" la quantité : l'offre mélange tous les produits de la catégorie
            bundle_prices.setdefault(item["category"], []).extend([unit_price] * item["qty"])
        else:
            total += unit_price * item["qty"]

    # Règle 2 : offre groupée par catégorie.
    # Tri décroissant puis tranches de N : la dernière unité de chaque tranche est
    # la moins chère et elle est offerte. Ce découpage maximise la remise pour le client.
    for prices in bundle_prices.values():
        prices.sort(reverse=True)
        total += sum(
            (p for i, p in enumerate(prices) if i % bundle_size != bundle_size - 1),
            Decimal("0"),
        )

    return float(total.quantize(CENT, rounding=ROUND_HALF_UP))


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
