import datetime as dt
import json

import boto3


def _dates_to_strings(dates: list[dt.date]) -> list[str]:
    return [d.isoformat() for d in dates]


def _strings_to_dates(strings: list[str]) -> list[dt.date]:
    return [dt.date.fromisoformat(x) for x in strings]


def read_dates_from_s3(bucket: str, key: str) -> list[dt.date]:
    s3 = boto3.client("s3")
    try:
        obj = s3.get_object(Bucket=bucket, Key=key)
        data = json.loads(obj["Body"].read())
        return _strings_to_dates(data)
    except s3.exceptions.NoSuchKey:
        return []


def write_dates_to_s3(bucket: str, key: str, dates: list[dt.date]) -> None:
    s3 = boto3.client("s3")
    s3.put_object(Bucket=bucket, Key=key, Body=json.dumps(_dates_to_strings(dates)))


class DateCache:
    def __init__(self, old_dates: list[dt.date]):
        self.old_dates = old_dates

    def find_new_dates(self, current_dates: list[dt.date]) -> list[dt.date]:
        return list(set(current_dates) - set(self.old_dates))
