"""
Lab 6 - Branch coverage tests for vending_machine.py

Goal: make every decision (if / while / for) evaluate to both True and False,
and probe the boundaries of each condition.
Run:
    coverage run --branch -m pytest BranchCoverageTest_vending_machine.py
    coverage report -m
"""
import pytest
from vending_machine import PRICES, COINS, select_item, make_change, purchase


# ---------------------------------------------------------------------------
# Starter examples + earlier line-coverage tests
# ---------------------------------------------------------------------------
def test_invalid_item():
    assert select_item("water", {}, 100) == "invalid"


def test_no_change_needed():
    assert make_change(0) == []


def test_select_item_sold_out():
    assert select_item("cola", {"cola": 0}, 200) == "sold_out"


def test_select_item_insufficient_credit():
    assert select_item("cola", {"cola": 5}, 100) == "insufficient"


def test_select_item_ok():
    assert select_item("cola", {"cola": 5}, 150) == "ok"


def test_make_change_negative_amount_raises():
    with pytest.raises(ValueError, match="negative amount"):
        make_change(-5)


def test_make_change_uses_every_denomination():
    assert make_change(190) == [100, 50, 25, 10, 5]


def test_make_change_not_possible_returns_none():
    assert make_change(3) is None


def test_purchase_rejected_returns_status_and_no_change():
    assert purchase("cola", {"cola": 0}, 200) == ("sold_out", [])


def test_purchase_no_exact_change_keeps_stock():
    stock = {"cola": 1}
    assert purchase("cola", stock, 153) == ("no_exact_change", [])
    assert stock["cola"] == 1


def test_purchase_dispensed_reduces_stock_and_returns_change():
    stock = {"chips": 2}
    assert purchase("chips", stock, 200) == ("dispensed", [100])
    assert stock["chips"] == 1


# ---------------------------------------------------------------------------
# select_item: each `if` taken both ways, plus boundaries
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("item", ["water", "", "COLA", "cola "])
def test_select_item_unknown_names_are_invalid(item):
    # `item not in PRICES` -> True. Even with plenty of stock and credit.
    assert select_item(item, {item: 10}, 1000) == "invalid"


@pytest.mark.parametrize("item", list(PRICES))
def test_select_item_known_items_pass_validity_check(item):
    # `item not in PRICES` -> False for every real item
    assert select_item(item, {item: 1}, PRICES[item]) == "ok"


def test_select_item_missing_stock_key_counts_as_sold_out():
    # stock.get(item, 0) falls back to 0 when the key is absent
    assert select_item("candy", {}, 500) == "sold_out"
    assert select_item("candy", {"cola": 9}, 500) == "sold_out"


def test_select_item_stock_of_one_is_available():
    # `stock == 0` -> False at the smallest non-zero value
    assert select_item("candy", {"candy": 1}, 75) == "ok"


def test_select_item_credit_exactly_equal_to_price_is_ok():
    # boundary of `credit < price`
    assert select_item("chips", {"chips": 3}, 100) == "ok"


def test_select_item_credit_one_below_price_is_insufficient():
    assert select_item("chips", {"chips": 3}, 99) == "insufficient"


def test_select_item_zero_credit_is_insufficient():
    assert select_item("candy", {"candy": 3}, 0) == "insufficient"


def test_select_item_sold_out_checked_before_credit():
    # sold-out AND no credit -> sold_out wins (order of the checks)
    assert select_item("cola", {"cola": 0}, 0) == "sold_out"


def test_select_item_invalid_checked_before_stock():
    assert select_item("water", {"water": 0}, 0) == "invalid"


# ---------------------------------------------------------------------------
# make_change: negative check, for-loop, while-loop, leftover check
# ---------------------------------------------------------------------------
def test_make_change_minus_one_raises_boundary():
    # boundary of `amount < 0`
    with pytest.raises(ValueError):
        make_change(-1)


def test_make_change_zero_skips_every_while_loop():
    # while condition False immediately for all coins; no leftover
    assert make_change(0) == []


@pytest.mark.parametrize("coin", COINS)
def test_make_change_single_coin_amounts(coin):
    # while-loop runs exactly once for the matching coin
    assert make_change(coin) == [coin]


@pytest.mark.parametrize(
    "amount, expected",
    [
        (105, [100, 5]),
        (35, [25, 10]),
        (20, [10, 10]),
        (15, [10, 5]),
        (75, [50, 25]),
        (300, [100, 100, 100]),   # while-loop repeats for the same coin
        (55, [50, 5]),
    ],
)
def test_make_change_combinations(amount, expected):
    assert make_change(amount) == expected


@pytest.mark.parametrize("amount", [1, 2, 3, 4, 6, 101, 153])
def test_make_change_leftover_below_smallest_coin_returns_none(amount):
    # `amount > 0` after the loop -> True
    assert make_change(amount) is None


def test_make_change_total_matches_amount():
    for amount in range(0, 400, 5):
        assert sum(make_change(amount)) == amount


# ---------------------------------------------------------------------------
# purchase: both outcomes of `status != "ok"` and `change is None`
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "item, stock, credit, expected_status",
    [
        ("water", {}, 500, "invalid"),
        ("cola", {"cola": 0}, 500, "sold_out"),
        ("cola", {}, 500, "sold_out"),
        ("cola", {"cola": 2}, 149, "insufficient"),
    ],
)
def test_purchase_rejection_statuses_pass_through(item, stock, credit, expected_status):
    before = dict(stock)
    assert purchase(item, stock, credit) == (expected_status, [])
    assert stock == before  # nothing dispensed, nothing changed


def test_purchase_exact_payment_gives_empty_change():
    stock = {"candy": 1}
    assert purchase("candy", stock, 75) == ("dispensed", [])
    assert stock["candy"] == 0


def test_purchase_dispensed_with_multi_coin_change():
    stock = {"cola": 4}
    # 300 - 150 = 150 -> 100 + 50
    assert purchase("cola", stock, 300) == ("dispensed", [100, 50])
    assert stock["cola"] == 3


def test_purchase_only_decrements_the_chosen_item():
    stock = {"cola": 3, "chips": 3, "candy": 3}
    purchase("chips", stock, 100)
    assert stock == {"cola": 3, "chips": 2, "candy": 3}


def test_purchase_no_exact_change_for_each_item():
    for item, price in PRICES.items():
        stock = {item: 1}
        assert purchase(item, stock, price + 2) == ("no_exact_change", [])
        assert stock[item] == 1


def test_purchase_last_unit_then_sold_out():
    stock = {"chips": 1}
    assert purchase("chips", stock, 100) == ("dispensed", [])
    assert purchase("chips", stock, 100) == ("sold_out", [])
    assert stock["chips"] == 0
