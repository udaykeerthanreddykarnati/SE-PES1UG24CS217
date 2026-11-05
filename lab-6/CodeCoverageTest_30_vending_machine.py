"""
Lab 6 - Code (line) coverage tests for vending_machine.py

Goal: execute every statement in vending_machine.py at least once.
Run:
    coverage run -m pytest CodeCoverageTest_vending_machine.py
    coverage report -m
"""
import pytest
from vending_machine import select_item, make_change, purchase


# ---------------------------------------------------------------------------
# Starter examples
# ---------------------------------------------------------------------------
def test_invalid_item():
    assert select_item("water", {}, 100) == "invalid"


def test_no_change_needed():
    assert make_change(0) == []


# ---------------------------------------------------------------------------
# select_item: one test per return statement
# ---------------------------------------------------------------------------
def test_select_item_sold_out():
    assert select_item("cola", {"cola": 0}, 200) == "sold_out"


def test_select_item_insufficient_credit():
    assert select_item("cola", {"cola": 5}, 100) == "insufficient"


def test_select_item_ok():
    assert select_item("cola", {"cola": 5}, 150) == "ok"


# ---------------------------------------------------------------------------
# make_change: raise, coin loop, and the "cannot make exact change" return
# ---------------------------------------------------------------------------
def test_make_change_negative_amount_raises():
    with pytest.raises(ValueError, match="negative amount"):
        make_change(-5)


def test_make_change_uses_every_denomination():
    # 190 = 100 + 50 + 25 + 10 + 5
    assert make_change(190) == [100, 50, 25, 10, 5]


def test_make_change_not_possible_returns_none():
    # smallest coin is 5, so 3 cannot be paid out
    assert make_change(3) is None


# ---------------------------------------------------------------------------
# purchase: rejected, no exact change, dispensed
# ---------------------------------------------------------------------------
def test_purchase_rejected_returns_status_and_no_change():
    assert purchase("cola", {"cola": 0}, 200) == ("sold_out", [])


def test_purchase_no_exact_change_keeps_stock():
    stock = {"cola": 1}
    # 153 - 150 = 3 left over, which no coin can cover
    assert purchase("cola", stock, 153) == ("no_exact_change", [])
    assert stock["cola"] == 1


def test_purchase_dispensed_reduces_stock_and_returns_change():
    stock = {"chips": 2}
    assert purchase("chips", stock, 200) == ("dispensed", [100])
    assert stock["chips"] == 1
