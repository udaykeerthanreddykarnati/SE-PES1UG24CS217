# Lab 7 — Fuzz Testing (`vending_machine.py`)

## Objective of Fuzz Testing

Fuzz testing (fuzzing) is a dynamic software testing technique that feeds random, unexpected, malformed, or boundary inputs into a program to uncover crashes, unhandled exceptions, input-validation flaws, logic bugs, and potential denial-of-service vectors that manual unit tests often overlook.

In this lab, fuzz testing is used to:
- Expose missing input validation and edge-case failures in a vending machine input-parsing module.
- Compare traditional deterministic unit tests (Lab 6) with property-based fuzz testing (Lab 7).
- Harden each function using explicit defensive checks rather than masking bugs with broad exception catching.

---

## Description of Hypothesis

[Hypothesis](https://hypothesis.readthedocs.io/) is a property-based testing and fuzzing library for Python. Instead of hardcoding individual input examples, you specify input generation strategies (`hypothesis.strategies`) and invariants/properties that must hold across all generated inputs using `@given(...)`.

Key capabilities used in this lab:
- **Automated test-case generation**: Explores hundreds of inputs per test using strategies such as `st.text()`, `st.none()`, `st.integers()`, `st.floats()`, `st.booleans()`, `st.lists()`, `st.dictionaries()`, `st.characters()`, and `st.tuples()`.
- **Shrinking**: Automatically reduces any failing input down to a minimal counterexample (such as `''`, `None`, `','`, `'0'`, `'ß'`, `'/'`, or `(-1, 0)`).
- **Deterministic fuzzing**: Configured via `settings(derandomize=True, max_examples=200, database=None, deadline=None)` so test runs remain reproducible.

---

## Functions Tested

All three functions in [`vending_machine.py`](./vending_machine.py) were tested:

1. **`parse_coins(coins_csv)`**  
   Parses a comma-separated string of coin values (e.g., `"5,10,25"`) into a list of integers (`[5, 10, 25]`).
2. **`slot_position(code)`**  
   Converts a vending machine slot code (e.g., `"B7"`) into a 0-based `(row, column)` tuple (`(1, 6)`).
3. **`change_due(payment)`**  
   Parses a `"<paid>/<price>"` string (e.g., `"200/150"`) and computes change in 5-unit coins (`"10 five-coins"`).

---

## Bugs Discovered & Minimal Failing Inputs

Running [`test_vending_machine.py`](./test_vending_machine.py) against the initial unvalidated implementation uncovered crashes and silent logic bugs in all three functions.

### 1. `parse_coins(coins_csv)`

| Bug Category | Minimal Failing Input | Observed Failure / Wrong Behavior |
|---|---|---|
| `None` / non-string type | `None` | `AttributeError: 'NoneType' object has no attribute 'split'` |
| Empty string | `""` | `ValueError: invalid literal for int() with base 10: ''` |
| Extra / trailing / missing separators | `","` | `ValueError: invalid literal for int() with base 10: ''` |
| Zero / negative coin values | `"0"` (`values=[0]`) | Silently returned `[0]` instead of rejecting |
| Unicode digits | `"٠"` | Silently accepted Arabic-Indic zero and returned `[0]` |
| Special / non-numeric characters | `":"` | `ValueError: invalid literal for int() with base 10: ':'` |
| Extremely large values (>4300 digits) | `"9" * 4301` | `ValueError: Exceeds the limit (4300 digits) for integer string conversion` |
| Unrealistically huge numeric values | `"10001"` | Silently returned `[10001]` |

### 2. `slot_position(code)`

| Bug Category | Minimal Failing Input | Observed Failure / Wrong Behavior |
|---|---|---|
| `None` / non-string types | `None`, `[0]`, `{}`, `[]` | `TypeError`, `AttributeError`, `KeyError`, `IndexError` |
| Empty string | `""` | `IndexError: string index out of range` |
| Single-character / missing column | `"0"`, `"A"`, `"   "` | `ValueError: invalid literal for int() with base 10` |
| Unicode case-expansion crash | `"ß1"` (`prefix='ß', col=1`) | `TypeError: ord() expected a character, but string of length 2 found` (`'ß'.upper() == 'SS'`) |
| Non-letter row prefix | `"01"` (`prefix='0', col=1`) | Silently returned negative row `(-17, 0)` |
| Zero / negative column | `"A0"` | Silently returned negative column `(0, -1)` |
| Internal whitespace | `"A 1"` | Silently returned `(0, 0)` |
| Extremely large column | `"A" + "9" * 4301`, `"A100001"` | `ValueError` (4300-digit limit) or silently returned `(0, 100000)` |

### 3. `change_due(payment)`

| Bug Category | Minimal Failing Input | Observed Failure / Wrong Behavior |
|---|---|---|
| `None` / non-string types | `None` | `AttributeError: 'NoneType' object has no attribute 'split'` |
| Empty string / missing `/` | `""` | `ValueError: not enough values to unpack (expected 2, got 1)` |
| Missing operand around `/` | `"/"` | `ValueError: invalid literal for int() with base 10: ''` |
| Extra `/` separator | `"//0"` (`bad_paid='/', price=0`) | `ValueError: too many values to unpack (expected 2, got 3)` |
| Non-numeric / special characters | `":/0"` | `ValueError: invalid literal for int() with base 10: ':'` |
| Negative amounts / insufficient payment | `"-1/0"` (`pair=(-1, 0)`) | Silently returned `"-1 five-coins"` |
| Extremely large values (>4300 digits) | `"9" * 4301 + "/0"` | `ValueError: Exceeds the limit (4300 digits) for integer string conversion` |
| Out-of-bounds payment amount | `"100001/0"` | Silently returned `"20000 five-coins"` |

---

## Fixes Implemented

In [`vending_machine.py`](./vending_machine.py), all three functions were hardened with explicit input validation and documented return values (`None` for invalid input; `[]` for empty/space-only coin CSV):

- **Shared ASCII integer parser (`_parse_ascii_int`)**:
  - Rejects empty strings and strings longer than `MAX_INTEGER_DIGITS` (`6`) *before* calling `int()`, eliminating 4300-digit conversion crashes.
  - Requires `token.isascii() and token.isdigit()` so Unicode numerals (`'٠'`), signs (`'+'`, `'-'`), underscores (`'1_000'`), decimals, and whitespace characters like `\n`/`\t` are rejected explicitly.
  - Enforces function-specific `[min_value, max_value]` bounds.
- **`parse_coins(coins_csv)`**:
  - Checks `isinstance(coins_csv, str)`; returns `[]` for `""` or space-only strings, and `None` for non-strings or malformed inputs.
  - Splits on `,`, strips ASCII spaces from each segment, and validates every segment is an integer in `[1, 10_000]` (rejecting `","`, `",5"`, `"5,"`, `"5,,10"`, `"5 10"`, negative values, and `0`).
- **`slot_position(code)`**:
  - Checks `isinstance(code, str)` and requires at least 2 characters after stripping surrounding ASCII spaces.
  - Validates the row prefix is a single ASCII letter (`isascii()` and `isalpha()`) before calling `.upper()` and `ord()`.
  - Validates the column suffix is an integer in `[1, 100]` with no internal whitespace or signs.
- **`change_due(payment)`**:
  - Checks `isinstance(payment, str)` and splits on `/` requiring exactly 2 parts.
  - Validates both `paid` and `price` are ASCII integers in `[0, 100_000]` and rejects insufficient payments where `paid < price`.
- **`main()` & `_prompt()`**:
  - Prints clear validation messages when `None` is returned and handles `EOFError` cleanly during interactive input without catching logic exceptions inside the tested functions.

---

## Before-Fix vs. After-Fix Test Results

### Before Fix
- Command: `python3 -m pytest lab-7/test_vending_machine.py -v --tb=no`
- Result: **`22 failed, 3 passed`** in `6.45s` (out of 25 tests; only the 3 valid-input preservation tests passed).
- Application run (`python3 lab-7/vending_machine.py`): succeeded on valid sample inputs (`5,10,25`, `B7`, `200/150`) but crashed with `ValueError` on malformed input (`5,,25`).

### After Fix
- Command: `python3 -m pytest lab-7/test_vending_machine.py -v`
- Result: **`25 passed`** in `2.35s` (all no-crash, type-check, separator, Unicode, negative/zero, large-value, and valid-input preservation tests pass).
- Application run (`python3 lab-7/vending_machine.py`): preserves exact output on valid inputs (`[5, 10, 25]`, `(1, 6)`, `10 five-coins`) and reports friendly validation errors without crashing on invalid inputs (`5,,25`, `ß1`, `100/200`).

---

## Screenshots

Full-screen terminal screenshots saved under [`screenshots/`](./screenshots/):

| File | Description |
|---|---|
| [`screenshots/before_app_output.png`](./screenshots/before_app_output.png) | Initial `vending_machine.py` run (valid sample run + `ValueError` crash on `5,,25`) |
| [`screenshots/before_pytest_failures.png`](./screenshots/before_pytest_failures.png) | Initial `pytest` output showing `22 failed, 3 passed` |
| [`screenshots/before_minimal_counterexamples.png`](./screenshots/before_minimal_counterexamples.png) | Hypothesis shrunk minimal counterexamples (`[0]`, `'ß1'`, `'01'`, `(-1, 0)`) |
| [`screenshots/after_app_output.png`](./screenshots/after_app_output.png) | Fixed `vending_machine.py` handling both valid and previously crashing inputs |
| [`screenshots/after_pytest_passing.png`](./screenshots/after_pytest_passing.png) | Final `pytest` output showing all `25 passed` |

---

## Submission PDF

- [`Lab7_FuzzTesting_PES1UG24CS217.pdf`](./Lab7_FuzzTesting_PES1UG24CS217.pdf) — Complete Lab 7 submission PDF containing the handout-ordered screenshots (Steps 2, 4, 5, and 6), discovered bugs/fixes table, fixed `vending_machine.py`, and updated `test_vending_machine.py`.

---

## Commands to Run the Project

From the repository root:

```bash
# Install dependencies (if not already installed)
pip3 install hypothesis pytest

# Run the interactive vending machine CLI
python3 lab-7/vending_machine.py

# Run the Hypothesis fuzz test suite
python3 -m pytest lab-7/test_vending_machine.py -v
```
