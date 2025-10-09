import datetime as dt
import json

import boto3


def _dates_to_strings(dates: list[dt.date]) -> list[str]:
    return [d.isoformat() for d in dates]


def _strings_to_dates(strings: list[str]) -> list[dt.date]:
    return [dt.date.fromisoformat(x) for x in strings]


class DateCache:
    def __init__(self, bucket: str, file: str):
        self.bucket = bucket
        self.key = file

    def load_old_dates(self) -> list[dt.date]:
        s3 = boto3.client("s3")
        try:
            obj = s3.get_object(Bucket=self.bucket, Key=self.key)
            data = json.loads(obj["Body"].read())
        except s3.exceptions.NoSuchKey:
            return []
        return _strings_to_dates(data)

    def save_dates(self, dates: list[dt.date]):
        s3 = boto3.client("s3")
        s3.put_object(Bucket=self.bucket, Key=self.key, Body=json.dumps(_dates_to_strings(dates)))
