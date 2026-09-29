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


# --- Cas limites ajoutés après revue ---


def test_lignes_du_meme_article_sont_regroupees(rules):
    # 2 lignes de 3 x A = 6 x A : la remise volume (>= 5) doit s'appliquer
    # 6 x 9€, puis 2 livres offerts -> 4 x 9€
    cart = [
        {"id": "A", "category": "book", "price": 10.0, "qty": 3},
        {"id": "A", "category": "book", "price": 10.0, "qty": 3},
    ]
    assert calculate_total(cart, rules) == 36.00


def test_meme_id_avec_prix_different_refuse(rules):
    cart = [
        {"id": "A", "category": "book", "price": 10.0, "qty": 1},
        {"id": "A", "category": "book", "price": 12.0, "qty": 1},
    ]
    with pytest.raises(ValueError):
        calculate_total(cart, rules)


@pytest.mark.parametrize("qty", [-1, -10])
def test_quantite_negative_refusee(rules, qty):
    with pytest.raises(ValueError):
        calculate_total([{"id": "X", "category": "tech", "price": 10.0, "qty": qty}], rules)


@pytest.mark.parametrize("qty", [1.5, "2", True])
def test_quantite_non_entiere_refusee(rules, qty):
    with pytest.raises(TypeError):
        calculate_total([{"id": "X", "category": "tech", "price": 10.0, "qty": qty}], rules)


def test_prix_negatif_refuse(rules):
    with pytest.raises(ValueError):
        calculate_total([{"id": "X", "category": "tech", "price": -5.0, "qty": 1}], rules)


def test_champ_manquant_refuse(rules):
    with pytest.raises(ValueError):
        calculate_total([{"id": "X", "category": "tech", "qty": 1}], rules)


def test_quantite_zero(rules):
    cart = [{"id": "X", "category": "book", "price": 10.0, "qty": 0}]
    assert calculate_total(cart, rules) == 0.0


def test_arrondi_au_centime_superieur(rules):
    # en float, round(1.005, 2) donne 1.0 ; en Decimal ROUND_HALF_UP -> 1.01
    cart = [{"id": "X", "category": "tech", "price": 1.005, "qty": 1}]
    assert calculate_total(cart, rules) == 1.01


def test_pas_d_erreur_de_float_sur_les_sommes(rules):
    cart = [
        {"id": "X", "category": "tech", "price": 0.1, "qty": 1},
        {"id": "Y", "category": "tech", "price": 0.2, "qty": 1},
    ]
    assert calculate_total(cart, rules) == 0.3


def test_decoupage_maximise_la_remise_client():
    # 30, 20, 10, 10, 5, 5 -> tranches (30,20,10) et (10,5,5) : 10 + 5 offerts
    rules = {"bundle_categories": ["book"]}
    cart = [
        {"id": p, "category": "book", "price": price, "qty": 1}
        for p, price in [("a", 30), ("b", 20), ("c", 10), ("d", 10), ("e", 5), ("f", 5)]
    ]
    assert calculate_total(cart, rules) == 65.00


def test_taille_de_pack_parametrable():
    # "4 pour 3" : sur 4 livres à 10€, 1 offert
    rules = {"bundle_categories": ["book"], "bundle_size": 4}
    cart = [{"id": "A", "category": "book", "price": 10.0, "qty": 4}]
    assert calculate_total(cart, rules) == 30.00


@pytest.mark.parametrize(
    "bad_rules",
    [
        {"volume_discounts": {5: 1.5}},
        {"volume_discounts": {5: -0.1}},
        {"volume_discounts": {0: 0.1}},
        {"bundle_size": 1},
    ],
)
def test_regles_invalides_refusees(bad_rules):
    with pytest.raises(ValueError):
        calculate_total([{"id": "A", "category": "book", "price": 10.0, "qty": 1}], bad_rules)
