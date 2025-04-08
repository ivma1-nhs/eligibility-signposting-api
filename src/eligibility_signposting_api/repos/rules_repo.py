import json
from typing import Annotated

from botocore.client import BaseClient
from wireup import Inject, service

from eligibility_signposting_api.model.rules import BucketName, Campaign, CampaignConfig, Rules


@service
class RulesRepo:
    def __init__(
        self,
        s3_client: Annotated[BaseClient, Inject(qualifier="s3")],
        bucket_name: Annotated[BucketName, Inject(param="rules_bucket_name")],
    ) -> None:
        super().__init__()
        self.s3_client = s3_client
        self.bucket_name = bucket_name

    def get_campaign_config(self, campaign: Campaign) -> CampaignConfig:
        response = self.s3_client.get_object(Bucket=self.bucket_name, Key=f"{campaign}.json")
        body = response["Body"].read()
        return Rules.model_validate(json.loads(body)).campaign_config
