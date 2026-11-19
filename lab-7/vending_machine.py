"""Vending machine input parsing and change calculation utilities."""

MAX_COIN_VALUE = 10_000
MAX_SLOT_COLUMN = 100
MAX_PAYMENT_AMOUNT = 100_000
MAX_INTEGER_DIGITS = 6


def _parse_ascii_int(token, min_value, max_value):
    """Parse an ASCII digit string within [min_value, max_value], or return None."""
    if not token or len(token) > MAX_INTEGER_DIGITS:
        return None
    if not (token.isascii() and token.isdigit()):
        return None
    value = int(token)
    if value < min_value or value > max_value:
        return None
    return value


def parse_coins(coins_csv):
    """Parse a comma-separated string of positive coin values.

    Returns a list of integers in [1, 10_000], [] for an empty or space-only
    string, or None for non-string, malformed, negative, or out-of-range input.
    """
    if not isinstance(coins_csv, str):
        return None
    if coins_csv.strip(" ") == "":
        return []

    coins = []
    for part in coins_csv.split(","):
        value = _parse_ascii_int(part.strip(" "), 1, MAX_COIN_VALUE)
        if value is None:
            return None
        coins.append(value)
    return coins


def slot_position(code):
    """Convert a slot code (e.g. 'B7') to 0-based (row, column), or None if invalid.

    Accepts a single ASCII row letter (A-Z, case-insensitive) followed by a
    1-based integer column in [1, 100].
    """
    if not isinstance(code, str):
        return None

    cleaned = code.strip(" ")
    if len(cleaned) < 2:
        return None

    row_char = cleaned[0]
    if not (row_char.isascii() and row_char.isalpha()):
        return None

    column_num = _parse_ascii_int(cleaned[1:], 1, MAX_SLOT_COLUMN)
    if column_num is None:
        return None

    row = ord(row_char.upper()) - ord("A")
    return row, column_num - 1


def change_due(payment):
    """Return change in five-coin units for a '<paid>/<price>' string, or None if invalid.

    Both paid and price must be non-negative ASCII integers in [0, 100_000]
    with paid >= price.
    """
    if not isinstance(payment, str):
        return None

    parts = payment.split("/")
    if len(parts) != 2:
        return None

    paid = _parse_ascii_int(parts[0].strip(" "), 0, MAX_PAYMENT_AMOUNT)
    price = _parse_ascii_int(parts[1].strip(" "), 0, MAX_PAYMENT_AMOUNT)
    if paid is None or price is None or paid < price:
        return None

    change = paid - price
    return f"{change // 5} five-coins"


def _prompt(message):
    """Read a line from standard input, returning None on EOF."""
    try:
        return input(message)
    except EOFError:
        return None


def main():
    """Run an interactive CLI demo for coin parsing, slot lookup, and change."""
    print("==== Running parse_coins ====")
    user_input = _prompt("Enter coin values as CSV (e.g. 5,10,25): ")
    coins = parse_coins(user_input)
    if coins is None:
        print("Invalid coin input. Enter positive integers separated by commas.")
    else:
        print("Coins:", coins)

    print("\n==== Running slot_position ====")
    user_input = _prompt("Enter a slot code (e.g. B7): ")
    position = slot_position(user_input)
    if position is None:
        print("Invalid slot code. Use format like B7 (row A-Z, column 1-100).")
    else:
        print("Row and Column:", position)

    print("\n==== Running change_due ====")
    user_input = _prompt("Enter paid/price (e.g. 200/150): ")
    change = change_due(user_input)
    if change is None:
        print("Invalid payment. Use '<paid>/<price>' with non-negative integers and paid >= price.")
    else:
        print("Change Due:", change)


if __name__ == "__main__":
    main()
