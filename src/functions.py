MONTHS = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
}


def get_month_number(month_name: str) -> int:
    return MONTHS[month_name.strip().lower()]


def get_year(year: str) -> int:
    if year.endswith("."):
        return int(year[:-1])
    else:
        return int(year)
