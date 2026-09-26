import pytest

from calculate_total import calculate_total


@pytest.fixture
def rules():
    return {
        "volume_discounts": {5: 0.10, 10: 0.20},
        "bundle_categories": ["book"],
    }


def test_exemple_de_l_enonce(rules):
    cart = [
        {"id": "A", "category": "book", "price": 10.0, "qty": 4},
        {"id": "B", "category": "book", "price": 15.0, "qty": 1},
        {"id": "C", "category": "tech", "price": 100.0, "qty": 1},
    ]
    assert calculate_total(cart, rules) == 145.00


def test_panier_vide(rules):
    assert calculate_total([], rules) == 0.0


def test_remise_volume_10(rules):
    cart = [{"id": "X", "category": "tech", "price": 10.0, "qty": 5}]
    assert calculate_total(cart, rules) == 45.00


def test_remise_volume_prend_le_plus_gros_seuil(rules):
    cart = [{"id": "X", "category": "tech", "price": 10.0, "qty": 10}]
    assert calculate_total(cart, rules) == 80.00


def test_pack_offre_le_moins_cher(rules):
    cart = [
        {"id": "A", "category": "book", "price": 10.0, "qty": 1},
        {"id": "B", "category": "book", "price": 20.0, "qty": 1},
        {"id": "C", "category": "book", "price": 30.0, "qty": 1},
    ]
    assert calculate_total(cart, rules) == 50.00


def test_volume_puis_pack(rules):
    # 6 livres à 10€ -> 9€ après -10%, puis 2 offerts -> 4 x 9€
    cart = [{"id": "A", "category": "book", "price": 10.0, "qty": 6}]
    assert calculate_total(cart, rules) == 36.00


def test_pas_de_pack_hors_categorie(rules):
    cart = [{"id": "X", "category": "tech", "price": 10.0, "qty": 3}]
    assert calculate_total(cart, rules) == 30.00


def test_packs_separes_par_categorie():
    rules = {"volume_discounts": {}, "bundle_categories": ["book", "dvd"]}
    cart = [
        {"id": "A", "category": "book", "price": 10.0, "qty": 2},
        {"id": "B", "category": "dvd", "price": 10.0, "qty": 1},
    ]
    # 2 livres + 1 dvd : aucune tranche de 3 dans une même catégorie
    assert calculate_total(cart, rules) == 30.00


def test_regles_vides():
    cart = [{"id": "A", "category": "book", "price": 10.0, "qty": 3}]
    assert calculate_total(cart, {}) == 30.00


def test_arrondi_deux_decimales(rules):
    cart = [{"id": "X", "category": "tech", "price": 0.1, "qty": 3}]
    assert calculate_total(cart, rules) == 0.30
