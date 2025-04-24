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


OPERATORS: dict[RuleOperator, type[OperatorRule]] = {RuleOperator.equals: Equals, RuleOperator.gt: GT}
