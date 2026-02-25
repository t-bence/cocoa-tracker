import datetime as dt
import logging

import requests
from bs4 import BeautifulSoup

from src.functions import get_month_number, get_year

logger = logging.getLogger()


def parse_html_content(html_content: str) -> list[dt.date]:
    soup = BeautifulSoup(html_content, "html.parser")
    articles = soup.find_all("article", class_="event")
    logger.info(f"Found {len(articles)} articles")

    dates: list[dt.date] = []
    for article in articles:
        event_fn_div = article.find("div", class_="event__fn")
        if not event_fn_div:
            logger.debug("No event__fn div found, skipping article.")
            continue
        event_name = event_fn_div.get_text(strip=True)
        if "sold out" in event_name.lower():
            continue
        year_div = article.find("div", class_="year")
        month_div = article.find("div", class_="month")
        day_div = article.find("div", class_="day")
        try:
            year = get_year(year_div.get_text(strip=True)) if year_div else 0
            month = get_month_number(month_div.get_text(strip=True)) if month_div else 0
            day = int(day_div.get_text(strip=True)) if day_div else 0
            date_obj = dt.date(year, month, day)
            dates.append(date_obj)
            logger.info(f"Added date: {date_obj} for event: {event_name}")
        except Exception as e:
            logger.warning(f"Failed to parse date for event '{event_name}': {e}")
            continue
    logger.info(f"Returning {len(dates)} dates")
    return dates


def fetch_concert_dates(url: str) -> list[dt.date]:
    logger.info(f"Requesting URL: {url}")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Network error while fetching URL {url}: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error while fetching URL {url}: {e}")
        return []
    return parse_html_content(response.text)
