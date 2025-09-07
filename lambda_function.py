import datetime as dt
import os

import requests
from bs4 import BeautifulSoup

from src.functions import get_month_number, get_year

url = "https://bfz.hu/en/concerts-tickets/concerts-and-festivals/cocoa-concerts/"


TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN", "")


def list_article_tags_content(url: str) -> list[dt.date]:
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    articles = soup.find_all("article")

    dates: list[dt.date] = []
    for article in articles:
        event_fn_div = article.find("div", class_="event__fn")
        if not event_fn_div:
            continue
        event_name = event_fn_div.get_text(strip=True)
        if "sold out" in event_name.lower():
            continue
        year_div = article.find("div", class_="year")
        month_div = article.find("div", class_="month")
        day_div = article.find("div", class_="day")
        year = get_year(year_div.get_text(strip=True)) if year_div else 0
        month = get_month_number(month_div.get_text(strip=True)) if month_div else 0
        day = int(day_div.get_text(strip=True)) if day_div else 0

        dates.append(dt.date(year, month, day))

    return dates


def send_message(dates: list[dt.date]) -> None:
    import boto3

    sns = boto3.client("sns")

    formatted_dates = [date.strftime("%Y-%m-%d") for date in dates]

    message = f"""Van hely kakaókoncertre!
    Dátum:
    {formatted_dates}"""

    sns.publish(
        TopicArn=TOPIC_ARN,
        Message=message,
    )


def lambda_handler(event, context):
    dates = list_article_tags_content(url)
    if dates:
        send_message(dates)


if __name__ == "__main__":
    print(list_article_tags_content(url))
