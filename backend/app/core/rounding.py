from decimal import Decimal, ROUND_HALF_UP

TWOPLACES = Decimal("0.01")


def round_money(val: Decimal | str | int) -> Decimal:
    """
    Rounds any money amount strictly using ROUND_HALF_UP to 2 decimal places.
    Never accepts float to prevent precision loss.
    """
    if isinstance(val, float):
        raise TypeError("Float is strictly disallowed for money calculations. Use Decimal or string.")
    d = Decimal(val) if not isinstance(val, Decimal) else val
    return d.quantize(TWOPLACES, rounding=ROUND_HALF_UP)


def format_inr(val: Decimal | str | int) -> str:
    """
    Formats a Decimal into Indian currency format (e.g. ₹1,25,000.00).
    Follows Indian digit grouping: last 3 digits, then pairs of 2 digits.
    """
    d = round_money(val)
    sign = "-" if d < 0 else ""
    d_abs = abs(d)
    parts = f"{d_abs:.2f}".split(".")
    integer_part = parts[0]
    decimal_part = parts[1]

    if len(integer_part) <= 3:
        formatted_int = integer_part
    else:
        last3 = integer_part[-3:]
        rest = integer_part[:-3]
        groups = []
        while len(rest) > 2:
            groups.insert(0, rest[-2:])
            rest = rest[:-2]
        if rest:
            groups.insert(0, rest)
        formatted_int = ",".join(groups) + "," + last3

    return f"{sign}₹{formatted_int}.{decimal_part}"

