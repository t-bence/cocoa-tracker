import datetime as dt
import json

import boto3


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
        return [dt.date(x) for x in data]

    def save_dates(self, dates: list[dt.date]):
        s3 = boto3.client("s3")
        s3.put_object(Bucket=self.bucket, Key=self.key, Body=json.dumps(dates))
