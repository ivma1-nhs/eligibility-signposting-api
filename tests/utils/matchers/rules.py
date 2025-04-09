from datetime import date

from brunns.matchers.utils import append_matcher_description, describe_field_match, describe_field_mismatch
from hamcrest import anything
from hamcrest.core.base_matcher import BaseMatcher
from hamcrest.core.description import Description
from hamcrest.core.helpers.wrap_matcher import wrap_matcher
from hamcrest.core.matcher import Matcher

from eligibility_signposting_api.model.rules import (
    CampaignConfig,
    CampaignID,
    CampaignName,
    CampaignVersion,
    EndDate,
    Iteration,
    IterationCohort,
    IterationID,
    IterationName,
    IterationRule,
    IterationVersion,
    RuleAttributeLevel,
    RuleAttributeName,
    RuleComparator,
    RuleDescription,
    RuleName,
    RuleOperator,
    RulePriority,
    RuleType,
    StartDate,
)

ANYTHING = anything()


class CampaignConfigMatcher(BaseMatcher[CampaignConfig]):
    def __init__(self) -> None:
        super().__init__()
        self.id_: Matcher[CampaignID] = ANYTHING
        self.version: Matcher[CampaignVersion] = ANYTHING
        self.name: Matcher[CampaignName] = ANYTHING
        self.type: Matcher[str] = ANYTHING
        self.target: Matcher[str] = ANYTHING
        self.manager: Matcher[str | None] = ANYTHING
        self.approver: Matcher[str | None] = ANYTHING
        self.reviewer: Matcher[str | None] = ANYTHING
        self.iteration_frequency: Matcher[str] = ANYTHING
        self.iteration_type: Matcher[str] = ANYTHING
        self.iteration_time: Matcher[str | None] = ANYTHING
        self.default_comms_routing: Matcher[str | None] = ANYTHING
        self.start_date: Matcher[StartDate] = ANYTHING
        self.end_date: Matcher[EndDate] = ANYTHING
        self.approval_minimum: Matcher[int | None] = ANYTHING
        self.approval_maximum: Matcher[int | None] = ANYTHING
        self.iterations: Matcher[list[Iteration] | None] = ANYTHING

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

    # Chainable setters
    def with_id(self, id_: CampaignID | Matcher[CampaignID]) -> "CampaignConfigMatcher":
        self.id_ = wrap_matcher(id_)
        return self

    def and_id(self, id_: CampaignID | Matcher[CampaignID]):
        return self.with_id(id_)

    def with_version(self, version: CampaignVersion | Matcher[CampaignVersion]) -> "CampaignConfigMatcher":
        self.version = wrap_matcher(version)
        return self

    def and_version(self, version: CampaignVersion | Matcher[CampaignVersion]):
        return self.with_version(version)

    def with_name(self, name: CampaignName | Matcher[CampaignName]) -> "CampaignConfigMatcher":
        self.name = wrap_matcher(name)
        return self

    def and_name(self, name: CampaignName | Matcher[CampaignName]):
        return self.with_name(name)

    def with_type(self, type_: str | Matcher[str]) -> "CampaignConfigMatcher":
        self.type = wrap_matcher(type_)
        return self

    def with_target(self, target: str | Matcher[str]) -> "CampaignConfigMatcher":
        self.target = wrap_matcher(target)
        return self

    def with_manager(self, manager: str | None | Matcher[str | None]) -> "CampaignConfigMatcher":
        self.manager = wrap_matcher(manager)
        return self

    def with_approver(self, approver: str | None | Matcher[str | None]) -> "CampaignConfigMatcher":
        self.approver = wrap_matcher(approver)
        return self

    def with_reviewer(self, reviewer: str | None | Matcher[str | None]) -> "CampaignConfigMatcher":
        self.reviewer = wrap_matcher(reviewer)
        return self

    def with_iteration_frequency(self, iteration_frequency: str | Matcher[str]) -> "CampaignConfigMatcher":
        self.iteration_frequency = wrap_matcher(iteration_frequency)
        return self

    def with_iteration_type(self, iteration_type: str | Matcher[str]) -> "CampaignConfigMatcher":
        self.iteration_type = wrap_matcher(iteration_type)
        return self

    def with_iteration_time(self, iteration_time: str | None | Matcher[str | None]) -> "CampaignConfigMatcher":
        self.iteration_time = wrap_matcher(iteration_time)
        return self

    def with_default_comms_routing(
        self, default_comms_routing: str | None | Matcher[str | None]
    ) -> "CampaignConfigMatcher":
        self.default_comms_routing = wrap_matcher(default_comms_routing)
        return self

    def with_start_date(self, start_date: date | Matcher[date]) -> "CampaignConfigMatcher":
        self.start_date = wrap_matcher(start_date)
        return self

    def with_end_date(self, end_date: date | Matcher[date]) -> "CampaignConfigMatcher":
        self.end_date = wrap_matcher(end_date)
        return self

    def with_approval_minimum(self, approval_minimum: int | None | Matcher[int | None]) -> "CampaignConfigMatcher":
        self.approval_minimum = wrap_matcher(approval_minimum)
        return self

    def with_approval_maximum(self, approval_maximum: int | None | Matcher[int | None]) -> "CampaignConfigMatcher":
        self.approval_maximum = wrap_matcher(approval_maximum)
        return self

    def with_iterations(
        self, iterations: list[Iteration] | None | Matcher[list[Iteration] | None]
    ) -> "CampaignConfigMatcher":
        self.iterations = wrap_matcher(iterations)
        return self


def is_campaign_config() -> Matcher[CampaignConfig]:
    return CampaignConfigMatcher()


class IterationMatcher(BaseMatcher[Iteration]):
    def __init__(self) -> None:
        super().__init__()
        self.id_: Matcher[IterationID] = ANYTHING
        self.name: Matcher[IterationName] = ANYTHING
        self.version: Matcher[IterationVersion] = ANYTHING
        self.iteration_date: Matcher[str | None] = ANYTHING
        self.iteration_number: Matcher[int | None] = ANYTHING
        self.comms_type: Matcher[str] = ANYTHING
        self.approval_minimum: Matcher[int | None] = ANYTHING
        self.approval_maximum: Matcher[int | None] = ANYTHING
        self.type: Matcher[str] = ANYTHING
        self.iteration_cohorts: Matcher[list[IterationCohort] | None] = ANYTHING
        self.iteration_rules: Matcher[list[IterationRule] | None] = ANYTHING
        self.default_comms_routing: Matcher[str | None] = ANYTHING

    def describe_to(self, description: Description) -> None:
        description.append_text("Iteration with")
        for attr in self.__dict__:
            if attr.startswith("_"):
                continue
            append_matcher_description(getattr(self, attr), attr.lstrip("_"), description)

    def _matches(self, item: Iteration) -> bool:
        return all(
            getattr(self, attr).matches(getattr(item, attr.lstrip("_")))
            for attr in self.__dict__
            if not attr.startswith("_")
        )

    def describe_mismatch(self, item: Iteration, mismatch_description: Description) -> None:
        mismatch_description.append_text("was Iteration with")
        for attr in self.__dict__:
            if attr.startswith("_"):
                continue
            describe_field_mismatch(
                getattr(self, attr), attr.lstrip("_"), getattr(item, attr.lstrip("_")), mismatch_description
            )

    def describe_match(self, item: Iteration, match_description: Description) -> None:
        match_description.append_text("was Iteration with")
        for attr in self.__dict__:
            if attr.startswith("_"):
                continue
            describe_field_match(
                getattr(self, attr), attr.lstrip("_"), getattr(item, attr.lstrip("_")), match_description
            )

    def with_id(self, id_: IterationID | Matcher[IterationID]) -> "IterationMatcher":
        self.id_ = wrap_matcher(id_)
        return self

    def with_name(self, name: IterationName | Matcher[IterationName]) -> "IterationMatcher":
        self.name = wrap_matcher(name)
        return self

    def with_version(self, version: IterationVersion | Matcher[IterationVersion]) -> "IterationMatcher":
        self.version = wrap_matcher(version)
        return self

    def with_iteration_date(self, iteration_date: str | Matcher[str]) -> "IterationMatcher":
        self.iteration_date = wrap_matcher(iteration_date)
        return self

    def with_iteration_number(self, iteration_number: int | Matcher[int]) -> "IterationMatcher":
        self.iteration_number = wrap_matcher(iteration_number)
        return self

    def with_comms_type(self, comms_type: str | Matcher[str]) -> "IterationMatcher":
        self.comms_type = wrap_matcher(comms_type)
        return self

    def with_approval_minimum(self, approval_minimum: int | Matcher[int]) -> "IterationMatcher":
        self.approval_minimum = wrap_matcher(approval_minimum)
        return self

    def with_approval_maximum(self, approval_maximum: int | Matcher[int]) -> "IterationMatcher":
        self.approval_maximum = wrap_matcher(approval_maximum)
        return self

    def with_type(self, type_: str | Matcher[str]) -> "IterationMatcher":
        self.type = wrap_matcher(type_)
        return self

    def with_iteration_cohorts(
        self, iteration_cohorts: list[IterationCohort] | Matcher[list[IterationCohort]]
    ) -> "IterationMatcher":
        self.iteration_cohorts = wrap_matcher(iteration_cohorts)
        return self

    def with_iteration_rules(
        self, iteration_rules: list[IterationRule] | Matcher[list[IterationRule]]
    ) -> "IterationMatcher":
        self.iteration_rules = wrap_matcher(iteration_rules)
        return self

    def with_default_comms_routing(self, default_comms_routing: str | Matcher[str]) -> "IterationMatcher":
        self.default_comms_routing = wrap_matcher(default_comms_routing)
        return self


def is_iteration() -> Matcher[Iteration]:
    return IterationMatcher()


class IterationRuleMatcher(BaseMatcher[IterationRule]):
    def __init__(self) -> None:
        super().__init__()
        self.type: Matcher[RuleType] = ANYTHING
        self.name: Matcher[RuleName] = ANYTHING
        self.description: Matcher[RuleDescription] = ANYTHING
        self.priority: Matcher[RulePriority] = ANYTHING
        self.attribute_level: Matcher[RuleAttributeLevel] = ANYTHING
        self.attribute_name: Matcher[RuleAttributeName] = ANYTHING
        self.operator: Matcher[RuleOperator] = ANYTHING
        self.comparator: Matcher[RuleComparator] = ANYTHING
        self.attribute_target: Matcher[str | None] = ANYTHING
        self.comms_routing: Matcher[str | None] = ANYTHING

    def describe_to(self, description: Description) -> None:
        description.append_text("IterationRule with")
        for attr in self.__dict__:
            if attr.startswith("_"):
                continue
            append_matcher_description(getattr(self, attr), attr, description)

    def _matches(self, item: IterationRule) -> bool:
        return all(
            getattr(self, attr).matches(getattr(item, attr)) for attr in self.__dict__ if not attr.startswith("_")
        )

    def describe_mismatch(self, item: IterationRule, mismatch_description: Description) -> None:
        mismatch_description.append_text("was IterationRule with")
        for attr in self.__dict__:
            if attr.startswith("_"):
                continue
            describe_field_mismatch(getattr(self, attr), attr, getattr(item, attr), mismatch_description)

    def describe_match(self, item: IterationRule, match_description: Description) -> None:
        match_description.append_text("was IterationRule with")
        for attr in self.__dict__:
            if attr.startswith("_"):
                continue
            describe_field_match(getattr(self, attr), attr, getattr(item, attr), match_description)

    def with_type(self, type_: RuleType | Matcher[RuleType]) -> "IterationRuleMatcher":
        self.type = wrap_matcher(type_)
        return self

    def with_name(self, name: RuleName | Matcher[RuleName]) -> "IterationRuleMatcher":
        self.name = wrap_matcher(name)
        return self

    def with_description(self, description_: RuleDescription | Matcher[RuleDescription]) -> "IterationRuleMatcher":
        self.description = wrap_matcher(description_)
        return self

    def with_priority(self, priority: RulePriority | Matcher[RulePriority]) -> "IterationRuleMatcher":
        self.priority = wrap_matcher(priority)
        return self

    def with_attribute_level(
        self, attribute_level: RuleAttributeLevel | Matcher[RuleAttributeLevel]
    ) -> "IterationRuleMatcher":
        self.attribute_level = wrap_matcher(attribute_level)
        return self

    def with_attribute_name(
        self, attribute_name: RuleAttributeName | Matcher[RuleAttributeName]
    ) -> "IterationRuleMatcher":
        self.attribute_name = wrap_matcher(attribute_name)
        return self

    def with_operator(self, operator: RuleOperator | Matcher[RuleOperator]) -> "IterationRuleMatcher":
        self.operator = wrap_matcher(operator)
        return self

    def with_comparator(self, comparator: RuleComparator | Matcher[RuleComparator]) -> "IterationRuleMatcher":
        self.comparator = wrap_matcher(comparator)
        return self

    def with_attribute_target(self, attribute_target: str | None | Matcher[str | None]) -> "IterationRuleMatcher":
        self.attribute_target = wrap_matcher(attribute_target)
        return self

    def with_comms_routing(self, comms_routing: str | None | Matcher[str | None]) -> "IterationRuleMatcher":
        self.comms_routing = wrap_matcher(comms_routing)
        return self


def is_iteration_rule() -> Matcher[IterationRule]:
    return IterationRuleMatcher()
