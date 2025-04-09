from brunns.matchers.utils import append_matcher_description, describe_field_match, describe_field_mismatch
from hamcrest import anything
from hamcrest.core.base_matcher import BaseMatcher
from hamcrest.core.description import Description
from hamcrest.core.helpers.wrap_matcher import wrap_matcher
from hamcrest.core.matcher import Matcher

from eligibility_signposting_api.model.rules import CampaignConfig, CampaignID, CampaignName, CampaignVersion

ANYTHING = anything()


class CampaignConfigMatcher(BaseMatcher[CampaignConfig]):
    def __init__(self):
        super().__init__()
        self.id_: Matcher[CampaignID] = ANYTHING
        self.name: Matcher[CampaignName] = ANYTHING
        self.version: Matcher[CampaignVersion] = ANYTHING

    def describe_to(self, description: Description) -> None:
        description.append_text("CampaignConfig with")
        append_matcher_description(self.id_, "id", description)
        append_matcher_description(self.name, "name", description)
        append_matcher_description(self.version, "version", description)

    def _matches(self, item: CampaignConfig) -> bool:
        return self.id_.matches(item.id) and self.name.matches(item.name) and self.version.matches(item.version)

    def describe_mismatch(self, item: CampaignConfig, mismatch_description: Description) -> None:
        mismatch_description.append_text("was CampaignConfig with")
        describe_field_mismatch(self.id_, "id", item.id, mismatch_description)
        describe_field_mismatch(self.name, "name", item.name, mismatch_description)
        describe_field_mismatch(self.version, "version", item.version, mismatch_description)

    def describe_match(self, item: CampaignConfig, match_description: Description) -> None:
        match_description.append_text("was CampaignConfig with")
        describe_field_match(self.id_, "id", item.id, match_description)
        describe_field_match(self.name, "name", item.name, match_description)
        describe_field_match(self.version, "version", item.version, match_description)

    def with_id(self, id_: CampaignID | Matcher[CampaignID]):
        self.id_ = wrap_matcher(id_)
        return self

    def and_id(self, id_: CampaignID | Matcher[CampaignID]):
        return self.with_id(id_)

    def with_name(self, name: CampaignName | Matcher[CampaignName]):
        self.name = wrap_matcher(name)
        return self

    def and_name(self, name: CampaignName | Matcher[CampaignName]):
        return self.with_name(name)

    def with_version(self, version: CampaignVersion | Matcher[CampaignVersion]):
        self.version = wrap_matcher(version)
        return self

    def and_version(self, version: CampaignVersion | Matcher[CampaignVersion]):
        return self.with_version(version)


def is_campaign_config() -> Matcher[CampaignConfig]:
    return CampaignConfigMatcher()
