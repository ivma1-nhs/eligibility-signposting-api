from hamcrest import anything
from hamcrest.core.matcher import Matcher

from eligibility_signposting_api.model.rules import CampaignConfig, Iteration, IterationRule

from .meta import BaseAutoMatcher

ANYTHING = anything()


class CampaignConfigMatcher(BaseAutoMatcher):
    __domain_class__ = CampaignConfig


def is_campaign_config() -> Matcher[CampaignConfig]:
    return CampaignConfigMatcher()


class IterationMatcher(BaseAutoMatcher):
    __domain_class__ = Iteration


def is_iteration() -> Matcher[Iteration]:
    return IterationMatcher()


class IterationRuleMatcher(BaseAutoMatcher):
    __domain_class__ = IterationRule


def is_iteration_rule() -> Matcher[IterationRule]:
    return IterationRuleMatcher()
