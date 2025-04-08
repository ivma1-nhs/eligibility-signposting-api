import json
from collections.abc import Generator

import pytest
from botocore.client import BaseClient
from hamcrest import assert_that

from eligibility_signposting_api.model.rules import BucketName, CampaignConfig
from eligibility_signposting_api.repos.rules_repo import RulesRepo
from tests.integration.conftest import AWS_REGION
from tests.utils.builders import CampaignConfigFactory, random_str
from tests.utils.rules.campaign import is_campaign_config


@pytest.fixture
def bucket(s3_client: BaseClient) -> Generator[BucketName]:
    bucket_name = BucketName(random_str(63))
    s3_client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={"LocationConstraint": AWS_REGION})
    yield bucket_name
    s3_client.delete_bucket(Bucket=bucket_name)


@pytest.fixture
def campaign(s3_client: BaseClient, bucket: BucketName) -> Generator[CampaignConfig]:
    campaign: CampaignConfig = CampaignConfigFactory.build()
    campaign_data = {"CampaignConfig": campaign.model_dump(by_alias=True)}
    s3_client.put_object(
        Bucket=bucket, Key=f"{campaign.name}.json", Body=json.dumps(campaign_data), ContentType="application/json"
    )
    yield campaign
    s3_client.delete_object(Bucket=bucket, Key=f"{campaign.name}.json")


def test_get_campaign_config(s3_client: BaseClient, bucket: BucketName, campaign: CampaignConfig):
    # Given
    repo = RulesRepo(s3_client, bucket)

    # When
    actual = repo.get_campaign_config(campaign.name)

    # Then
    assert_that(actual, is_campaign_config().with_id(campaign.id).and_name(campaign.name).and_version(campaign.version))
