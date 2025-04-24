import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import ClassVar

from hamcrest.core.base_matcher import BaseMatcher

from eligibility_signposting_api.model.rules import RuleOperator

logger = logging.getLogger(__name__)


@dataclass
class OperatorRule(BaseMatcher[str], ABC):
    rule_comparator: str
    rule_operator: ClassVar[RuleOperator]

    @abstractmethod
    def _matches(self, item: str) -> bool: ...


class OperatorRegistry:
    registry: ClassVar[dict[RuleOperator, type[OperatorRule]]] = {}

    @staticmethod
    def register(the_type: type[OperatorRule]) -> type[OperatorRule]:
        OperatorRegistry.registry[the_type.rule_operator] = the_type
        return the_type


@OperatorRegistry.register
class Equals(OperatorRule):
    rule_operator: ClassVar[RuleOperator] = RuleOperator.equals

    def _matches(self, item: str) -> bool:
        return item == self.rule_comparator


@OperatorRegistry.register
class GT(OperatorRule):
    rule_operator: ClassVar[RuleOperator] = RuleOperator.gt

    def _matches(self, item: str) -> bool:
        return bool(item) and int(item) > int(self.rule_comparator)


@OperatorRegistry.register
class LT(OperatorRule):
    rule_operator: ClassVar[RuleOperator] = RuleOperator.lt

    def _matches(self, item: str) -> bool:
        return bool(item) and int(item) < int(self.rule_comparator)


@OperatorRegistry.register
class NE(OperatorRule):
    rule_operator: ClassVar[RuleOperator] = RuleOperator.ne

    def _matches(self, item: str) -> bool:
        return bool(item) and item != self.rule_comparator


@OperatorRegistry.register
class GTE(OperatorRule):
    rule_operator: ClassVar[RuleOperator] = RuleOperator.gte

    def _matches(self, item: str) -> bool:
        return bool(item) and int(item) >= int(self.rule_comparator)


@OperatorRegistry.register
class LTE(OperatorRule):
    rule_operator: ClassVar[RuleOperator] = RuleOperator.lte

    def _matches(self, item: str) -> bool:
        return bool(item) and int(item) <= int(self.rule_comparator)


@OperatorRegistry.register
class Contains(OperatorRule):
    rule_operator: ClassVar[RuleOperator] = RuleOperator.contains

    def _matches(self, item: str) -> bool:
        return bool(item) and self.rule_comparator in str(item)


@OperatorRegistry.register
class NotContains(OperatorRule):
    rule_operator: ClassVar[RuleOperator] = RuleOperator.not_contains

    def _matches(self, item: str) -> bool:
        return self.rule_comparator not in str(item)


@OperatorRegistry.register
class StartsWith(OperatorRule):
    rule_operator: ClassVar[RuleOperator] = RuleOperator.starts_with

    def _matches(self, item: str) -> bool:
        return str(item).startswith(self.rule_comparator)


@OperatorRegistry.register
class NotStartsWith(OperatorRule):
    rule_operator: ClassVar[RuleOperator] = RuleOperator.not_starts_with

    def _matches(self, item: str) -> bool:
        return not str(item).startswith(self.rule_comparator)
