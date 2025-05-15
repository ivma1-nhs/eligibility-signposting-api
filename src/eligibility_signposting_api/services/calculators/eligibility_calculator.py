from __future__ import annotations

from _operator import attrgetter
from collections import defaultdict
from collections.abc import Collection, Iterator, Mapping
from dataclasses import dataclass, field
from functools import cached_property
from itertools import groupby
from typing import Any

from wireup import service

from eligibility_signposting_api.model import eligibility, rules
from eligibility_signposting_api.services.calculators.rule_calculator import RuleCalculator

Row = Collection[Mapping[str, Any]]


@service
class EligibilityCalculatorFactory:
    @staticmethod
    def get(person_data: Row, campaign_configs: Collection[rules.CampaignConfig]) -> EligibilityCalculator:
        return EligibilityCalculator(person_data=person_data, campaign_configs=campaign_configs)


@dataclass
class EligibilityCalculator:
    person_data: Row
    campaign_configs: Collection[rules.CampaignConfig]

    results: dict[eligibility.ConditionName, eligibility.Condition] = field(default_factory=dict)

    @cached_property
    def condition_names(self) -> set[eligibility.ConditionName]:
        return {
            eligibility.ConditionName(cc.target)
            for cc in self.campaign_configs
            if cc.campaign_live and cc.current_iteration
        }

    def evaluate_eligibility(self) -> eligibility.EligibilityStatus:
        """Calculate a person's eligibility for vaccination."""

        # Get all iterations for which the person is base eligible, i.e. those which *might* provide eligibility
        # due to cohort membership.
        base_eligible_campaigns = self.get_base_eligible_campaigns()

        # Evaluate iteration rules to see if the person is actionable, not actionable (due to "F" rules),
        # or not eligible (due to "S" rules")
        evaluations = self.evaluate_for_base_eligible_campaigns(base_eligible_campaigns)

        # Add all not base eligible conditions to result set.
        self.get_not_base_eligible_conditions(base_eligible_campaigns)
        # Add all base eligible conditions to result set.
        self.get_base_eligible_conditions(evaluations)

        return eligibility.EligibilityStatus(conditions=list(self.results.values()))

    def get_base_eligible_campaigns(self) -> list[rules.CampaignConfig]:
        """Get all campaigns for which the person is base eligible, i.e. those which *might* provide eligibility.

        Build and return a collection of campaigns for which the person is base eligible (using cohorts).
        Also build and return a set of conditions in the campaigns while we are here.
        """
        base_eligible_campaigns: list[rules.CampaignConfig] = []

        for campaign_config in (cc for cc in self.campaign_configs if cc.campaign_live and cc.current_iteration):
            base_eligible = self.evaluate_base_eligibility(campaign_config.current_iteration)
            if base_eligible:
                base_eligible_campaigns.append(campaign_config)

        return base_eligible_campaigns

    def evaluate_base_eligibility(self, iteration: rules.Iteration | None) -> set[str]:
        """Return cohorts for which person is base eligible."""
        if not iteration:
            return set()
        iteration_cohorts: set[str] = {
            cohort.cohort_label for cohort in iteration.iteration_cohorts if cohort.cohort_label
        }

        cohorts_row: Mapping[str, dict[str, dict[str, dict[str, Any]]]] = next(
            (r for r in self.person_data if r.get("ATTRIBUTE_TYPE", "") == "COHORTS"), {}
        )
        person_cohorts = set(cohorts_row.get("COHORT_MAP", {}).get("cohorts", {}).get("M", {}).keys())

        return iteration_cohorts.intersection(person_cohorts)

    def get_not_base_eligible_conditions(
        self,
        base_eligible_campaigns: Collection[rules.CampaignConfig],
    ) -> None:
        """Get conditions where the person is not base eligible,
        i.e. is not is the cohort for any campaign iteration."""

        # for each condition:
        # if the person isn't base eligible for any iteration,
        #         the person is not (base) eligible for the condition
        for condition_name in self.condition_names:
            if condition_name not in {eligibility.ConditionName(cc.target) for cc in base_eligible_campaigns}:
                self.results[condition_name] = eligibility.Condition(
                    condition_name=condition_name, status=eligibility.Status.not_eligible, reasons=[]
                )

    def evaluate_for_base_eligible_campaigns(
        self, base_eligible_campaigns: Collection[rules.CampaignConfig]
    ) -> dict[eligibility.ConditionName, dict[eligibility.Status, list[eligibility.Reason]]]:
        """Evaluate iteration rules to see if the person is actionable, not actionable (due to "F" rules),
        or not eligible (due to "S" rules").

        For each condition, evaluate all iterations for inclusion or exclusion."""
        priority_getter = attrgetter("priority")

        base_eligible_evaluations: dict[
            eligibility.ConditionName, dict[eligibility.Status, list[eligibility.Reason]]
        ] = defaultdict(dict)
        for condition_name, iteration in [
            (eligibility.ConditionName(cc.target), cc.current_iteration)
            for cc in base_eligible_campaigns
            if cc.current_iteration
        ]:
            # Until we see a worse status, we assume someone is actionable for this iteration.
            worst_status_so_far_for_condition = eligibility.Status.actionable
            exclusion_reasons, actionable_reasons = [], []
            for _priority, iteration_rule_group in groupby(
                sorted(iteration.iteration_rules, key=priority_getter), key=priority_getter
            ):
                worst_status_so_far_for_condition, group_actionable_reasons, group_exclusion_reasons = (
                    self.evaluate_priority_group(iteration_rule_group, worst_status_so_far_for_condition)
                )
                actionable_reasons.extend(group_actionable_reasons)
                exclusion_reasons.extend(group_exclusion_reasons)
            condition_entry = base_eligible_evaluations.setdefault(condition_name, {})
            condition_status_entry = condition_entry.setdefault(worst_status_so_far_for_condition, [])
            condition_status_entry.extend(
                actionable_reasons
                if worst_status_so_far_for_condition is eligibility.Status.actionable
                else exclusion_reasons
            )
        return base_eligible_evaluations

    def evaluate_priority_group(
        self,
        iteration_rule_group: Iterator[rules.IterationRule],
        worst_status_so_far_for_condition: eligibility.Status,
    ) -> tuple[eligibility.Status, list[eligibility.Reason], list[eligibility.Reason]]:
        actionable_reasons, exclusion_reasons = [], []
        exclude_capable_rules = [
            ir for ir in iteration_rule_group if ir.type in (rules.RuleType.filter, rules.RuleType.suppression)
        ]
        best_status_so_far_for_priority_group = (
            eligibility.Status.not_eligible if exclude_capable_rules else eligibility.Status.actionable
        )
        for iteration_rule in exclude_capable_rules:
            rule_calculator = RuleCalculator(person_data=self.person_data, rule=iteration_rule)
            status, reason = rule_calculator.evaluate_exclusion()
            if status.is_exclusion:
                best_status_so_far_for_priority_group = eligibility.Status.best(
                    status, best_status_so_far_for_priority_group
                )
                exclusion_reasons.append(reason)
            else:
                best_status_so_far_for_priority_group = eligibility.Status.actionable
                actionable_reasons.append(reason)
        return (
            eligibility.Status.worst(best_status_so_far_for_priority_group, worst_status_so_far_for_condition),
            actionable_reasons,
            exclusion_reasons,
        )

    def get_base_eligible_conditions(
        self,
        base_eligible_evaluations: Mapping[
            eligibility.ConditionName, Mapping[eligibility.Status, list[eligibility.Reason]]
        ],
    ) -> None:
        """Get conditions where the person is base eligible, but may be either actionable, not actionable,
        or not eligible."""

        # for each condition for which the person is base eligible:
        #   what is the "best" status, i.e. closest to actionable? Add the condition to the result with that status.
        for condition_name, reasons_by_status in base_eligible_evaluations.items():
            best_status = eligibility.Status.best(*list(reasons_by_status.keys()))
            self.results[condition_name] = eligibility.Condition(
                condition_name=condition_name, status=best_status, reasons=reasons_by_status[best_status]
            )
