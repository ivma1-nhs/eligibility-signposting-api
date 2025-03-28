import logging
import os
from functools import lru_cache
from typing import Any, NewType

from pythonjsonlogger.json import JsonFormatter
from yarl import URL

LOG_LEVEL = logging.getLevelNamesMapping().get(os.getenv("LOG_LEVEL", ""), logging.WARNING)

AwsRegion = NewType("AwsRegion", str)
AwsAccessKey = NewType("AwsAccessKey", str)
AwsSecretAccessKey = NewType("AwsSecretAccessKey", str)


@lru_cache
def config() -> dict[str, Any]:
    return {
        "aws_access_key_id": AwsAccessKey(os.getenv("AWS_ACCESS_KEY_ID", "dummy_key")),
        "aws_default_region": AwsRegion(os.getenv("AWS_DEFAULT_REGION", "eu-west-1")),
        "aws_endpoint_url": URL(os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566")),
        "aws_secret_access_key": AwsSecretAccessKey(os.getenv("AWS_SECRET_ACCESS_KEY", "dummy_secret")),
        "log_level": LOG_LEVEL,
    }


def init_logging() -> None:
    log_format = "%(asctime)s %(levelname)-8s %(name)s %(module)s.py:%(funcName)s():%(lineno)d %(message)s"
    formatter = JsonFormatter(log_format)
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logging.basicConfig(level=LOG_LEVEL, format=log_format, handlers=[handler])
