import datetime as dt
import logging

import boto3

logger = logging.getLogger()


def send_sns_notification(dates: list[dt.date], topic_arn: str) -> None:
    logger.info(f"Preparing to send message for {len(dates)} dates")
    sns = boto3.client("sns")

    formatted_dates: str = "\n".join([date.strftime("%Y-%m-%d") for date in dates])

    message = f"""Van hely kakaókoncertre!
Dátumok:
{formatted_dates}"""

    try:
        response = sns.publish(
            TopicArn=topic_arn,
            Message=message,
        )
        logger.info(f"SNS publish response: {response}")
    except Exception as e:
        logger.error(f"Failed to send SNS message: {e}")
