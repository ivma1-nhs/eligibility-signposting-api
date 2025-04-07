import json
import uuid
from collections.abc import Generator

import pytest
from botocore.client import BaseClient

from eligibility_signposting_api.model.rules import BucketName, Campaign
from eligibility_signposting_api.repos.rules_repo import RulesRepo
from tests.integration.conftest import AWS_REGION
from tests.utils.builders import random_int, random_str


@pytest.fixture
def bucket(s3_client: BaseClient) -> Generator[BucketName]:
    bucket_name = BucketName(random_str(63))
    s3_client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={"LocationConstraint": AWS_REGION})
    yield bucket_name
    s3_client.delete_bucket(Bucket=bucket_name)


@pytest.fixture
def campaign(s3_client: BaseClient, bucket: BucketName) -> Generator[Campaign]:
    campaign = Campaign(random_str(10))
    campaign_data = {
        "CampaignConfig": {"ID": f"{uuid.uuid4()}", "Version": random_int(maximum=10), "Name": random_str(10)}
    }
    s3_client.put_object(
        Bucket=bucket, Key=f"{campaign}.json", Body=json.dumps(campaign_data), ContentType="application/json"
    )
    yield campaign
    s3_client.delete_object(Bucket=bucket, Key=f"{campaign}.json")


def test_get_campaign_config(s3_client: BaseClient, bucket: BucketName, campaign: Campaign):
    # Given
    repo = RulesRepo(s3_client, bucket)

    # When
    actual = repo.get_campaign_config(campaign)

    # Then
    assert actual is not None
