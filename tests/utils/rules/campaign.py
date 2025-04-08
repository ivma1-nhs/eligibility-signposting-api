from brunns.matchers.utils import append_matcher_description, describe_field_match, describe_field_mismatch
from hamcrest import anything
from hamcrest.core.base_matcher import BaseMatcher
from hamcrest.core.description import Description
from hamcrest.core.helpers.wrap_matcher import wrap_matcher
from hamcrest.core.matcher import Matcher

from eligibility_signposting_api.model.rules import CampaignConfig

ANYTHING = anything()


class CampaignConfigMatcher(BaseMatcher[CampaignConfig]):
    def __init__(self):
        super().__init__()
        self.id_: Matcher[str] = ANYTHING

    def describe_to(self, description: Description) -> None:
        description.append_text("CampaignConfig with")
        append_matcher_description(self.id_, "id", description)

    def _matches(self, item: CampaignConfig) -> bool:
        return self.id_.matches(item.id)

    def describe_mismatch(self, item: CampaignConfig, mismatch_description: Description) -> None:
        mismatch_description.append_text("was CampaignConfig with")
        describe_field_mismatch(self.id_, "id", item.id, mismatch_description)

    def describe_match(self, item: CampaignConfig, match_description: Description) -> None:
        match_description.append_text("was CampaignConfig with")
        describe_field_match(self.id_, "id", item.id, match_description)

    def with_id(self, id_: str | Matcher[str]):
        self.id_ = wrap_matcher(id_)
        return self

    def and_id(self, id_: str | Matcher[str]):
        return self.with_id(id_)


def is_campaign_config() -> Matcher[CampaignConfig]:
    return CampaignConfigMatcher()
