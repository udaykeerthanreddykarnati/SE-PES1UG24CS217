"""
Lab 7 - Property-based fuzz tests for vending_machine.py using Hypothesis.
"""

from hypothesis import given, settings, strategies as st
import pytest

from vending_machine import change_due, parse_coins, slot_position

FUZZ_SETTINGS = settings(derandomize=True, max_examples=200, database=None, deadline=None)

UNEXPECTED_NON_STRINGS = st.one_of(
    st.none(),
    st.integers(),
    st.floats(allow_nan=True),
    st.booleans(),
    st.lists(st.integers(), max_size=4),
    st.dictionaries(st.text(max_size=4), st.integers(), max_size=3),
)

LARGE_NUMBER_STRINGS = st.one_of(
    st.integers(min_value=100_001, max_value=10**25).map(str),
    st.integers(min_value=4301, max_value=4600).map(lambda n: "9" * n),
)


# ---------------------------------------------------------------------------
# parse_coins(coins_csv)
# ---------------------------------------------------------------------------
@FUZZ_SETTINGS
@given(st.text() | st.none())
def test_parse_coins_no_crash(s):
    try:
        result = parse_coins(s)
    except Exception as exc:
        pytest.fail(f"parse_coins crashed on {s!r}: {type(exc).__name__}: {exc}")
    assert result is None or (
        isinstance(result, list)
        and all(type(item) is int and 1 <= item <= 10_000 for item in result)
    )


@FUZZ_SETTINGS
@given(st.text())
def test_parse_coins_arbitrary_text_no_crash(s):
    try:
        result = parse_coins(s)
    except Exception as exc:
        pytest.fail(f"parse_coins crashed on {s!r}: {type(exc).__name__}: {exc}")
    assert result is None or (
        isinstance(result, list)
        and all(type(item) is int and 1 <= item <= 10_000 for item in result)
    )


@FUZZ_SETTINGS
@given(UNEXPECTED_NON_STRINGS)
def test_parse_coins_unexpected_types_return_none(value):
    assert parse_coins(value) is None


@FUZZ_SETTINGS
@given(
    st.one_of(
        st.just(","),
        st.just(",5"),
        st.just("5,"),
        st.lists(st.sampled_from(["", " ", "5", "10"]), min_size=2, max_size=5)
        .filter(lambda parts: any(p.strip() == "" for p in parts) and any(p.strip() != "" for p in parts))
        .map(",".join),
        st.lists(st.integers(min_value=1, max_value=100), min_size=2, max_size=4).map(
            lambda nums: " ".join(str(n) for n in nums)
        ),
    )
)
def test_parse_coins_rejects_missing_or_extra_separators(coins_csv):
    assert parse_coins(coins_csv) is None


@FUZZ_SETTINGS
@given(st.lists(st.integers(max_value=0), min_size=1, max_size=5))
def test_parse_coins_rejects_negative_and_zero_values(values):
    coins_csv = ",".join(str(v) for v in values)
    assert parse_coins(coins_csv) is None


@FUZZ_SETTINGS
@given(
    st.one_of(
        st.text(min_size=1).filter(
            lambda s: s.strip() != "" and not all(ch in "0123456789, " for ch in s)
        ),
        st.sampled_from(["١", "٥,١٠", "²", "1_000", "+5", "5;10", "5|10", "5.0", "€5"]),
    )
)
def test_parse_coins_rejects_unicode_and_special_characters(coins_csv):
    assert parse_coins(coins_csv) is None


@FUZZ_SETTINGS
@given(
    st.one_of(
        st.integers(min_value=10_001, max_value=10**25).map(str),
        st.integers(min_value=4301, max_value=4600).map(lambda n: "9" * n),
    )
)
def test_parse_coins_rejects_extremely_large_values(large_coin):
    assert parse_coins(large_coin) is None


@FUZZ_SETTINGS
@given(st.lists(st.integers(min_value=1, max_value=10_000), min_size=1, max_size=10))
def test_parse_coins_preserves_valid_inputs(coins):
    coins_csv = ",".join(str(c) for c in coins)
    assert parse_coins(coins_csv) == coins
    spaced_csv = ", ".join(str(c) for c in coins)
    assert parse_coins(spaced_csv) == coins


def test_parse_coins_empty_string_returns_empty_list():
    assert parse_coins("") == []
    assert parse_coins("   ") == []


# ---------------------------------------------------------------------------
# slot_position(code)
# ---------------------------------------------------------------------------
@FUZZ_SETTINGS
@given(st.text() | st.none())
def test_slot_position_no_crash(s):
    try:
        result = slot_position(s)
    except Exception as exc:
        pytest.fail(f"slot_position crashed on {s!r}: {type(exc).__name__}: {exc}")
    assert result is None or (
        isinstance(result, tuple)
        and len(result) == 2
        and all(type(n) is int for n in result)
        and 0 <= result[0] <= 25
        and 0 <= result[1] <= 99
    )


@FUZZ_SETTINGS
@given(st.text())
def test_slot_position_arbitrary_text_no_crash(s):
    try:
        result = slot_position(s)
    except Exception as exc:
        pytest.fail(f"slot_position crashed on {s!r}: {type(exc).__name__}: {exc}")
    assert result is None or (
        isinstance(result, tuple)
        and len(result) == 2
        and all(type(n) is int for n in result)
        and 0 <= result[0] <= 25
        and 0 <= result[1] <= 99
    )


@FUZZ_SETTINGS
@given(UNEXPECTED_NON_STRINGS)
def test_slot_position_unexpected_types_return_none(value):
    assert slot_position(value) is None


@FUZZ_SETTINGS
@given(
    st.one_of(
        st.sampled_from(list("0123456789!@#$%^&*()-_=+[]{}|;:,./? ßﬁﬀéαΩ")),
        st.characters(min_codepoint=128),
    ),
    st.integers(min_value=1, max_value=20),
)
def test_slot_position_rejects_invalid_and_unicode_row_prefixes(prefix, col):
    assert slot_position(f"{prefix}{col}") is None


@FUZZ_SETTINGS
@given(
    st.sampled_from("ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
    st.one_of(
        st.just(""),
        st.just("0"),
        st.integers(max_value=-1).map(str),
        st.sampled_from(["+1", "1_0", "1.5", "abc", " 1", "١", "A1", "-"]),
    ),
)
def test_slot_position_rejects_invalid_columns(row_char, bad_col):
    assert slot_position(f"{row_char}{bad_col}") is None


@FUZZ_SETTINGS
@given(
    st.sampled_from("ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
    LARGE_NUMBER_STRINGS,
)
def test_slot_position_rejects_extremely_large_columns(row_char, large_col):
    assert slot_position(f"{row_char}{large_col}") is None


@FUZZ_SETTINGS
@given(st.sampled_from(["", "   ", "A", "1", "1A", "AA1", "A 1", "A,1", "A-1", "B7/1"]))
def test_slot_position_rejects_malformed_formats(code):
    assert slot_position(code) is None


@FUZZ_SETTINGS
@given(
    st.sampled_from("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"),
    st.integers(min_value=1, max_value=100),
)
def test_slot_position_preserves_valid_codes(row_char, col_num):
    expected = (ord(row_char.upper()) - ord("A"), col_num - 1)
    assert slot_position(f"{row_char}{col_num}") == expected


# ---------------------------------------------------------------------------
# change_due(payment)
# ---------------------------------------------------------------------------
@FUZZ_SETTINGS
@given(st.text() | st.none())
def test_change_due_no_crash(s):
    try:
        result = change_due(s)
    except Exception as exc:
        pytest.fail(f"change_due crashed on {s!r}: {type(exc).__name__}: {exc}")
    assert result is None or (isinstance(result, str) and result.endswith(" five-coins"))


@FUZZ_SETTINGS
@given(st.text())
def test_change_due_arbitrary_text_no_crash(s):
    try:
        result = change_due(s)
    except Exception as exc:
        pytest.fail(f"change_due crashed on {s!r}: {type(exc).__name__}: {exc}")
    assert result is None or (isinstance(result, str) and result.endswith(" five-coins"))


@FUZZ_SETTINGS
@given(UNEXPECTED_NON_STRINGS)
def test_change_due_unexpected_types_return_none(value):
    assert change_due(value) is None


@FUZZ_SETTINGS
@given(
    st.one_of(
        st.just(""),
        st.just("/"),
        st.just("200/"),
        st.just("/150"),
        st.integers(min_value=0, max_value=500).map(str),
        st.lists(st.integers(min_value=0, max_value=500).map(str), min_size=3, max_size=5).map("/".join),
        st.tuples(st.integers(min_value=0, max_value=500), st.integers(min_value=0, max_value=500)).map(
            lambda p: f"{p[0]},{p[1]}"
        ),
    )
)
def test_change_due_rejects_missing_or_extra_separators(payment):
    assert change_due(payment) is None


@FUZZ_SETTINGS
@given(
    st.one_of(
        st.tuples(st.integers(max_value=-1), st.integers(min_value=0, max_value=500)),
        st.tuples(st.integers(min_value=0, max_value=500), st.integers(max_value=-1)),
        st.tuples(st.integers(max_value=-1), st.integers(max_value=-1)),
        st.integers(min_value=0, max_value=500).flatmap(
            lambda paid: st.tuples(st.just(paid), st.integers(min_value=paid + 1, max_value=paid + 500))
        ),
    )
)
def test_change_due_rejects_negative_and_insufficient_payments(pair):
    paid, price = pair
    assert change_due(f"{paid}/{price}") is None


@FUZZ_SETTINGS
@given(
    st.one_of(
        st.text(min_size=1).filter(
            lambda s: s.strip() != "" and not all(ch in "0123456789 " for ch in s)
        ),
        st.sampled_from(["abc", "200.5", "+200", "2_00", "٢٠٠", "€20", "10 0", "NaN"]),
    ),
    st.integers(min_value=0, max_value=200),
)
def test_change_due_rejects_unicode_and_non_numeric_values(bad_paid, price):
    assert change_due(f"{bad_paid}/{price}") is None
    assert change_due(f"{price}/{bad_paid}") is None


@FUZZ_SETTINGS
@given(
    LARGE_NUMBER_STRINGS,
    st.integers(min_value=0, max_value=1000),
)
def test_change_due_rejects_extremely_large_values(large_amount, other):
    assert change_due(f"{large_amount}/{other}") is None
    assert change_due(f"{other}/{large_amount}") is None


@FUZZ_SETTINGS
@given(
    st.integers(min_value=0, max_value=50_000),
    st.integers(min_value=0, max_value=50_000),
)
def test_change_due_preserves_valid_inputs(price, extra):
    paid = price + extra
    assert change_due(f"{paid}/{price}") == f"{extra // 5} five-coins"
    assert change_due(f" {paid} / {price} ") == f"{extra // 5} five-coins"
