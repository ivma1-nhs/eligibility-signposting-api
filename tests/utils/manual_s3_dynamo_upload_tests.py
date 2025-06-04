import os
import json
import tempfile
import subprocess
from pathlib import Path
import pytest

import boto3
from moto import mock_aws

from scripts.manual_uploads.manual_s3_dynamo_upload import run_upload


@pytest.fixture
def test_data_dir(tmp_path):
    data = {"ID_NUMBER": "123", "ATTRIBUTE_TYPE": "Test", "value": 99}
    file_path = tmp_path / "test.json"
    with open(file_path, "w") as f:
        json.dump(data, f)
    return tmp_path, data


@mock_aws
def test_script_cli_end_to_end(test_data_dir, capsys):
    # Arrange
    data_dir, expected_data = test_data_dir
    env = "test"
    region = "eu-west-2"
    s3_bucket = f"api-{env}-rules"
    dynamo_table = f"api-{env}-datastore"

    s3 = boto3.client("s3", region_name=region)
    s3.create_bucket(
        Bucket=s3_bucket,
        CreateBucketConfiguration={"LocationConstraint": region}
    )

    dynamodb = boto3.client("dynamodb", region_name=region)
    dynamodb.create_table(
        TableName=dynamo_table,
        KeySchema=[
            {"AttributeName": "ID_NUMBER", "KeyType": "HASH"},
            {"AttributeName": "ATTRIBUTE_TYPE", "KeyType": "RANGE"}
        ],
        AttributeDefinitions=[
            {"AttributeName": "ID_NUMBER", "AttributeType": "S"},
            {"AttributeName": "ATTRIBUTE_TYPE", "AttributeType": "S"}
        ],
        BillingMode="PAY_PER_REQUEST"
    )

    # Act
    return_code = run_upload([
        "--env", env,
        "--upload-s3", str(data_dir),
        "--upload-dynamo", str(data_dir),
        "--region", region,
        "--s3-bucket", s3_bucket,
        "--dynamo-table", dynamo_table
    ])
    captured = capsys.readouterr()

    # Assert
    key = f"manual-uploads/test.json"
    obj = s3.get_object(Bucket=s3_bucket, Key=key)
    uploaded_s3_data = json.load(obj["Body"])
    assert uploaded_s3_data == expected_data

    item = dynamodb.get_item(
        TableName=dynamo_table,
        Key={
            "ID_NUMBER": {"S": expected_data["ID_NUMBER"]},
            "ATTRIBUTE_TYPE": {"S": expected_data["ATTRIBUTE_TYPE"]}
        }
    )["Item"]
    assert item["value"]["N"] == "99"

    assert "Uploaded" in captured.out
    assert "Error" not in captured.err
