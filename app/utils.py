import re


def parse_currency(amount: str) -> float:
    cleaned = re.sub(r"[^\d.,-]", "", amount)
    cleaned = cleaned.replace(",", "")
    return float(cleaned)
