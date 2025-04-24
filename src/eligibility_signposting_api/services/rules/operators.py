import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass

from hamcrest.core.base_matcher import BaseMatcher

from eligibility_signposting_api.model.rules import RuleOperator

logger = logging.getLogger(__name__)


@dataclass
class OperatorRule(BaseMatcher[str], ABC):
    rule_comparator: str

    @abstractmethod
    def _matches(self, item: str) -> bool: ...


class Equals(OperatorRule):
    def _matches(self, item: str) -> bool:
        return item == self.rule_comparator


class GT(OperatorRule):
    def _matches(self, item: str) -> bool:
        return bool(item) and int(item) > int(self.rule_comparator)


class LT(OperatorRule):
    def _matches(self, item: str) -> bool:
        return bool(item) and int(item) < int(self.rule_comparator)


class NE(OperatorRule):
    def _matches(self, item: str) -> bool:
        return bool(item) and item != self.rule_comparator


class GTE(OperatorRule):
    def _matches(self, item: str) -> bool:
        return bool(item) and int(item) >= int(self.rule_comparator)


class LTE(OperatorRule):
    def _matches(self, item: str) -> bool:
        return bool(item) and int(item) <= int(self.rule_comparator)


class Contains(OperatorRule):
    def _matches(self, item: str) -> bool:
        return item and self.rule_comparator in str(item)


class NotContains(OperatorRule):
    def _matches(self, item: str) -> bool:
        return self.rule_comparator not in str(item)


class StartsWith(OperatorRule):
    def _matches(self, item: str) -> bool:
        return str(item).startswith(self.rule_comparator)


class NotStartsWith(OperatorRule):
    def _matches(self, item: str) -> bool:
        return not str(item).startswith(self.rule_comparator)


OPERATORS: dict[RuleOperator, type[OperatorRule]] = {
    RuleOperator.equals: Equals,
    RuleOperator.gt: GT,
    RuleOperator.lt: LT,
    RuleOperator.ne: NE,
    RuleOperator.gte: GTE,
    RuleOperator.lte: LTE,
    RuleOperator.contains: Contains,
    RuleOperator.not_contains: NotContains,
    RuleOperator.starts_with: StartsWith,
    RuleOperator.not_starts_with: NotStartsWith,
}
