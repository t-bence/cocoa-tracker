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
    try:
        return MONTHS[month_name.strip().lower()]
    except KeyError:
        raise ValueError(f"Unknown month name: {month_name}")


def get_year(year: str) -> int:
    # Remove trailing dot if present and convert to int
    clean_year = year.strip().rstrip(".")
    try:
        return int(clean_year)
    except ValueError:
        raise ValueError(f"Could not parse year from script: {year}")
