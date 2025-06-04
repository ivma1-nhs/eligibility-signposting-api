import boto3
import hashlib
import json
import os
import argparse
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Generator
from decimal import Decimal


def map_dynamo_type(value: Any) -> Dict[str, Any]:
    if isinstance(value, str):
        return {"S": value}
    elif isinstance(value, bool):
        return {"BOOL": value}
    elif isinstance(value, (int, float, Decimal)):
        return {"N": str(value)}
    elif value is None:
        return {"NULL": True}
    elif isinstance(value, list):
        return {"L": [map_dynamo_type(item) for item in value]}
    elif isinstance(value, dict):
        return {"M": {k: map_dynamo_type(v) for k, v in value.items()}}
    elif isinstance(value, Row):
        return {"M": {k: map_dynamo_type(v) for k, v in value.asDict().items()}}
    else:
        logging.warning(f"Unsupported value type: {type(value)}", "Converting it to string")
        return {"S": value}


def load_json_lines(filepath: Union[str, Path]) -> Generator[Dict[str, Any], None, None]:
    with open(filepath) as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def upload_to_s3(
    s3_client: Any,
    bucket: str,
    filepath: Union[str, Path],
    dry_run: bool = False
) -> None:

    filename = os.path.basename(filepath)
    print(f"Filepath: {filepath}")
    s3_key = f"manual-uploads/{filename}"

    if dry_run:
        print(f"[DRY RUN] Would upload {filepath} to s3://{bucket}/{s3_key}")
        return

    try:
        s3_client.upload_file(filepath, bucket, s3_key)
        print(f"Uploaded {filepath} to s3://{bucket}/{s3_key}")
    except Exception as e:
        print(f"Failed to upload {filepath}: {e}")


def upload_to_dynamo(
    dynamo_client: Any,
    table_name: str,
    filepath: Union[str, Path],
) -> None:

    for item in load_json_lines(filepath):
        try:
            dynamo_client.put_item(
                TableName=table_name, Item={key: map_dynamo_type(value) for key, value in item.items()}
            )
            print(f"Uploaded {filepath} to DynamoDB table {table_name}")
        except Exception as e:
            print(f"Failed to upload {filepath}: {e}")


def run_upload(args: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env")
    parser.add_argument("--upload-s3", type=Path)
    parser.add_argument("--upload-dynamo", type=Path)
    parser.add_argument("--region", default="eu-west-2")
    parser.add_argument("--s3-bucket")
    parser.add_argument("--dynamo-table")
    parser.add_argument("--dry-run", action="store_true")

    if args is None:
        parsed_args = parser.parse_args()
    else:
        parsed_args = parser.parse_args(args)

    if not parsed_args.s3_bucket:
        parsed_args.s3_bucket = f"eligibility-signposting-api-{parsed_args.env}-eli-rules"
    if not parsed_args.dynamo_table:
        parsed_args.dynamo_table = f"eligibility-signposting-api-{parsed_args.env}-eligibility_datastore"

    session = boto3.Session()
    s3 = session.client("s3", region_name=parsed_args.region)
    dynamo = session.client("dynamodb", region_name=parsed_args.region)

    if parsed_args.upload_s3:
        for filepath in parsed_args.upload_s3.glob("*.json"):
            upload_to_s3(s3, parsed_args.s3_bucket, str(filepath), parsed_args.dry_run)

    if parsed_args.upload_dynamo:
        for filepath in parsed_args.upload_dynamo.glob("*.json"):
            upload_to_dynamo(dynamo, parsed_args.dynamo_table, str(filepath))


if __name__ == "__main__":
    run_upload()
