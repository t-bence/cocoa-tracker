import datetime as dt
import logging
import os

import requests
from bs4 import BeautifulSoup

from src.functions import get_month_number, get_year
from src.storage import DateCache

url = "https://bfz.hu/en/concerts-tickets/concerts-and-festivals/cocoa-concerts/"

TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN", "")

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def list_article_tags_content(url: str) -> list[dt.date]:
    logger.info(f"Requesting URL: {url}")
    try:
        response = requests.get(url)
        response.raise_for_status()
    except Exception as e:
        logger.error(f"Failed to fetch URL {url}: {e}")
        return []
    soup = BeautifulSoup(response.text, "html.parser")
    articles = soup.find_all("article")
    logger.info(f"Found {len(articles)} articles")

    dates: list[dt.date] = []
    for article in articles:
        event_fn_div = article.find("div", class_="event__fn")
        if not event_fn_div:
            logger.debug("No event__fn div found, skipping article.")
            continue
        event_name = event_fn_div.get_text(strip=True)
        if "sold out" in event_name.lower():
            logger.info(f"Skipping sold out event: {event_name}")
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


def send_message(dates: list[dt.date]) -> None:
    import boto3

    logger.info(f"Preparing to send message for {len(dates)} dates")
    sns = boto3.client("sns")

    formatted_dates: str = "\n".join([date.strftime("%Y-%m-%d") for date in dates])

    message = f"""Van hely kakaókoncertre!
    Dátumok:
    {formatted_dates}"""

    try:
        response = sns.publish(
            TopicArn=TOPIC_ARN,
            Message=message,
        )
        logger.info(f"SNS publish response: {response}")
    except Exception as e:
        logger.error(f"Failed to send SNS message: {e}")


def lambda_handler(event, context):
    logger.info("Lambda handler started")
    current_dates = list_article_tags_content(url)

    bucket = os.environ.get("BUCKET", "")
    file = "dates.json"

    cache = DateCache(bucket=bucket, file=file)
    old_dates = cache.load_old_dates()

    dates = set(current_dates) - set(old_dates)
    if dates:
        logger.info("Dates found, sending message")
        send_message(dates)
        cache.save_dates(current_dates)
    else:
        logger.info("No dates found, nothing to send")


if __name__ == "__main__":
    logger.info("Running as script")
    dates = list_article_tags_content(url)
    logger.info(f"Dates: {dates}")
