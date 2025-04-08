import json
import uuid
from collections.abc import Generator

import pytest
from botocore.client import BaseClient
from hamcrest import assert_that

from eligibility_signposting_api.model.rules import BucketName, Campaign
from eligibility_signposting_api.repos.rules_repo import RulesRepo
from tests.integration.conftest import AWS_REGION
from tests.utils.builders import random_int, random_str
from tests.utils.rules.campaign import is_campaign_config


@pytest.fixture
def bucket(s3_client: BaseClient) -> Generator[BucketName]:
    bucket_name = BucketName(random_str(63))
    s3_client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={"LocationConstraint": AWS_REGION})
    yield bucket_name
    s3_client.delete_bucket(Bucket=bucket_name)


@pytest.fixture
def campaign(s3_client: BaseClient, bucket: BucketName) -> Generator[tuple[Campaign, str, str]]:
    campaign_name = Campaign(random_str(10))
    id_ = f"{uuid.uuid4()}"
    version = random_int(maximum=10)
    campaign_data = {"CampaignConfig": {"ID": id_, "Version": version, "Name": campaign_name}}
    s3_client.put_object(
        Bucket=bucket, Key=f"{campaign_name}.json", Body=json.dumps(campaign_data), ContentType="application/json"
    )
    yield campaign_name, id_, version
    s3_client.delete_object(Bucket=bucket, Key=f"{campaign_name}.json")


def test_get_campaign_config(s3_client: BaseClient, bucket: BucketName, campaign: tuple[Campaign, str, str]):
    # Given
    campaign_name, id_, version = campaign
    repo = RulesRepo(s3_client, bucket)

    # When
    actual = repo.get_campaign_config(campaign_name)

    # Then
    assert_that(actual, is_campaign_config().with_id(id_).and_name(campaign_name).and_version(version))
