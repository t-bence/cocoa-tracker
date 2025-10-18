import logging
import os

from src.notifications import send_sns_notification
from src.scraper import fetch_concert_dates
from src.storage import DateCache, read_dates_from_s3, write_dates_to_s3

url = "https://bfz.hu/en/concerts-tickets/concerts-and-festivals/cocoa-concerts/"

TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN", "")

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info("Lambda handler started")
    current_dates = fetch_concert_dates(url)

    bucket = os.environ.get("BUCKET", "")
    file = "dates.json"

    old_dates = read_dates_from_s3(bucket, file)
    cache = DateCache(old_dates)
    new_dates = cache.find_new_dates(current_dates)

    if new_dates:
        logger.info("Dates found, sending message")
        send_sns_notification(new_dates, TOPIC_ARN)
        write_dates_to_s3(bucket, file, current_dates)
    else:
        logger.info("No dates found, nothing to send")


if __name__ == "__main__":
    logger.info("Running as script")
    dates = fetch_concert_dates(url)
    logger.info(f"Dates: {dates}")
