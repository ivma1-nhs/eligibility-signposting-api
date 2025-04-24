import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date, datetime
from typing import ClassVar

from dateutil.relativedelta import relativedelta
from hamcrest.core.base_matcher import BaseMatcher

from eligibility_signposting_api.model.rules import RuleOperator

AttributeData = str | int | bool | None
logger = logging.getLogger(__name__)


@dataclass
class OperatorRule(BaseMatcher[AttributeData], ABC):
    rule_comparator: str
    rule_operator: ClassVar[RuleOperator]

    @abstractmethod
    def _matches(self, item: AttributeData) -> bool: ...


class OperatorRegistry:
    registry: ClassVar[dict[RuleOperator, type[OperatorRule]]] = {}

    @staticmethod
    def register(the_type: type[OperatorRule]) -> type[OperatorRule]:
        OperatorRegistry.registry[the_type.rule_operator] = the_type
        return the_type

    @staticmethod
    def get(rule_operator: RuleOperator) -> type[OperatorRule]:
        if matcher_class := OperatorRegistry.registry.get(rule_operator):
            return matcher_class
        msg = f"{rule_operator} not implemented"
        raise NotImplementedError(msg)


@OperatorRegistry.register
class Equals(OperatorRule):
    rule_operator: ClassVar[RuleOperator] = RuleOperator.equals

    def _matches(self, item: AttributeData) -> bool:
        return item == self.rule_comparator


@OperatorRegistry.register
class GT(OperatorRule):
    rule_operator: ClassVar[RuleOperator] = RuleOperator.gt

    def _matches(self, item: AttributeData) -> bool:
        return bool(item) and int(item) > int(self.rule_comparator)


@OperatorRegistry.register
class LT(OperatorRule):
    rule_operator: ClassVar[RuleOperator] = RuleOperator.lt

    def _matches(self, item: AttributeData) -> bool:
        return bool(item) and int(item) < int(self.rule_comparator)


@OperatorRegistry.register
class NE(OperatorRule):
    rule_operator: ClassVar[RuleOperator] = RuleOperator.ne

    def _matches(self, item: AttributeData) -> bool:
        return bool(item) and item != self.rule_comparator


@OperatorRegistry.register
class GTE(OperatorRule):
    rule_operator: ClassVar[RuleOperator] = RuleOperator.gte

    def _matches(self, item: AttributeData) -> bool:
        return bool(item) and int(item) >= int(self.rule_comparator)


@OperatorRegistry.register
class LTE(OperatorRule):
    rule_operator: ClassVar[RuleOperator] = RuleOperator.lte

    def _matches(self, item: AttributeData) -> bool:
        return bool(item) and int(item) <= int(self.rule_comparator)


@OperatorRegistry.register
class Contains(OperatorRule):
    rule_operator: ClassVar[RuleOperator] = RuleOperator.contains

    def _matches(self, item: AttributeData) -> bool:
        return bool(item) and self.rule_comparator in str(item)


@OperatorRegistry.register
class NotContains(OperatorRule):
    rule_operator: ClassVar[RuleOperator] = RuleOperator.not_contains

    def _matches(self, item: AttributeData) -> bool:
        return self.rule_comparator not in str(item)


@OperatorRegistry.register
class StartsWith(OperatorRule):
    rule_operator: ClassVar[RuleOperator] = RuleOperator.starts_with

    def _matches(self, item: AttributeData) -> bool:
        return str(item).startswith(self.rule_comparator)


@OperatorRegistry.register
class NotStartsWith(OperatorRule):
    rule_operator: ClassVar[RuleOperator] = RuleOperator.not_starts_with

    def _matches(self, item: AttributeData) -> bool:
        return not str(item).startswith(self.rule_comparator)


@OperatorRegistry.register
class EndsWith(OperatorRule):
    rule_operator: ClassVar[RuleOperator] = RuleOperator.ends_with

    def _matches(self, item: AttributeData) -> bool:
        return str(item).endswith(self.rule_comparator)


@OperatorRegistry.register
class IsIn(OperatorRule):
    rule_operator: ClassVar[RuleOperator] = RuleOperator.is_in

    def _matches(self, item: AttributeData) -> bool:
        comparators = str(self.rule_comparator).split(",")
        return str(item) in comparators


@OperatorRegistry.register
class NotIn(OperatorRule):
    rule_operator: ClassVar[RuleOperator] = RuleOperator.not_in

    def _matches(self, item: AttributeData) -> bool:
        comparators = str(self.rule_comparator).split(",")
        return str(item) not in comparators


@OperatorRegistry.register
class MemberOf(OperatorRule):
    rule_operator: ClassVar[RuleOperator] = RuleOperator.member_of

    def _matches(self, item: AttributeData) -> bool:
        attribute_values = str(item).split(",")
        return self.rule_comparator in attribute_values


@OperatorRegistry.register
class NotMemberOf(OperatorRule):
    rule_operator: ClassVar[RuleOperator] = RuleOperator.not_member_of

    def _matches(self, item: AttributeData) -> bool:
        attribute_values = str(item).split(",")
        return self.rule_comparator not in attribute_values


@OperatorRegistry.register
class IsNull(OperatorRule):
    rule_operator: ClassVar[RuleOperator] = RuleOperator.is_null

    def _matches(self, item: AttributeData) -> bool:
        return item in (None, "")


@OperatorRegistry.register
class IsNotNull(OperatorRule):
    rule_operator: ClassVar[RuleOperator] = RuleOperator.is_not_null

    def _matches(self, item: AttributeData) -> bool:
        return item not in (None, "")


@OperatorRegistry.register
class Between(OperatorRule):
    rule_operator: ClassVar[RuleOperator] = RuleOperator.between

    def _matches(self, item: AttributeData) -> bool:
        if item in (None, ""):
            return False
        low_comparator_str, high_comparator_str = str(self.rule_comparator).split(",")
        low_comparator = min(int(low_comparator_str), int(high_comparator_str))
        high_comparator = max(int(low_comparator_str), int(high_comparator_str))
        return low_comparator <= int(item) <= high_comparator


@OperatorRegistry.register
class NotBetween(OperatorRule):
    rule_operator: ClassVar[RuleOperator] = RuleOperator.not_between

    def _matches(self, item: AttributeData) -> bool:
        if item in (None, ""):
            return False
        low_comparator_str, high_comparator_str = str(self.rule_comparator).split(",")
        low_comparator = min(int(low_comparator_str), int(high_comparator_str))
        high_comparator = max(int(low_comparator_str), int(high_comparator_str))
        return int(item) < low_comparator or int(item) > high_comparator


@OperatorRegistry.register
class IsEmpty(OperatorRule):
    rule_operator: ClassVar[RuleOperator] = RuleOperator.is_empty

    def _matches(self, item: AttributeData) -> bool:
        return item is None or all(item.strip() == "" for item in str(item).split(","))


@OperatorRegistry.register
class IsNotEmpty(OperatorRule):
    rule_operator: ClassVar[RuleOperator] = RuleOperator.is_not_empty

    def _matches(self, item: AttributeData) -> bool:
        return item is not None and any(item.strip() != "" for item in str(item).split(","))


@OperatorRegistry.register
class IsTrue(OperatorRule):
    rule_operator: ClassVar[RuleOperator] = RuleOperator.is_true

    def _matches(self, item: AttributeData) -> bool:
        return item is True


@OperatorRegistry.register
class IsFalse(OperatorRule):
    rule_operator: ClassVar[RuleOperator] = RuleOperator.is_false

    def _matches(self, item: AttributeData) -> bool:
        return item is False


class DateOperator(OperatorRule, ABC):
    @property
    def today(self) -> date:
        return date.today()  # noqa: DTZ011

    @staticmethod
    def get_attribute_date(item: AttributeData) -> date | None:
        return datetime.strptime(str(item), "%Y%m%d").date() if item else None  # noqa: DTZ007


class DateDayOperator(DateOperator, ABC):
    @property
    def cutoff(self) -> date:
        return self.today + relativedelta(days=int(self.rule_comparator))


@OperatorRegistry.register
class DayLTE(DateDayOperator):
    rule_operator: ClassVar[RuleOperator] = RuleOperator.day_lte

    def _matches(self, item: AttributeData) -> bool:
        attribute_date = self.get_attribute_date(item)
        return (attribute_date <= self.cutoff) if attribute_date else False


@OperatorRegistry.register
class DayLT(DateDayOperator):
    rule_operator: ClassVar[RuleOperator] = RuleOperator.day_lt

    def _matches(self, item: AttributeData) -> bool:
        attribute_date = self.get_attribute_date(item)
        return (attribute_date < self.cutoff) if attribute_date else False


@OperatorRegistry.register
class DayGTE(DateDayOperator):
    rule_operator: ClassVar[RuleOperator] = RuleOperator.day_gte

    def _matches(self, item: AttributeData) -> bool:
        attribute_date = self.get_attribute_date(item)
        return (attribute_date >= self.cutoff) if attribute_date else False


@OperatorRegistry.register
class DayGT(DateDayOperator):
    rule_operator: ClassVar[RuleOperator] = RuleOperator.day_gt

    def _matches(self, item: AttributeData) -> bool:
        attribute_date = self.get_attribute_date(item)
        return (attribute_date > self.cutoff) if attribute_date else False


class DateWeekOperator(DateOperator, ABC):
    @property
    def cutoff(self) -> date:
        return self.today + relativedelta(weeks=int(self.rule_comparator))


@OperatorRegistry.register
class WeekLTE(DateWeekOperator):
    rule_operator: ClassVar[RuleOperator] = RuleOperator.week_lte

    def _matches(self, item: AttributeData) -> bool:
        attribute_date = self.get_attribute_date(item)
        return (attribute_date <= self.cutoff) if attribute_date else False


@OperatorRegistry.register
class WeekLT(DateWeekOperator):
    rule_operator: ClassVar[RuleOperator] = RuleOperator.week_lt

    def _matches(self, item: AttributeData) -> bool:
        attribute_date = self.get_attribute_date(item)
        return (attribute_date < self.cutoff) if attribute_date else False


@OperatorRegistry.register
class WeekGTE(DateWeekOperator):
    rule_operator: ClassVar[RuleOperator] = RuleOperator.week_gte

    def _matches(self, item: AttributeData) -> bool:
        attribute_date = self.get_attribute_date(item)
        return (attribute_date >= self.cutoff) if attribute_date else False


@OperatorRegistry.register
class WeekGT(DateWeekOperator):
    rule_operator: ClassVar[RuleOperator] = RuleOperator.week_gt

    def _matches(self, item: AttributeData) -> bool:
        attribute_date = self.get_attribute_date(item)
        return (attribute_date > self.cutoff) if attribute_date else False


class DateYearOperator(DateOperator, ABC):
    @property
    def cutoff(self) -> date:
        return self.today + relativedelta(years=int(self.rule_comparator))


@OperatorRegistry.register
class YearLTE(DateYearOperator):
    rule_operator: ClassVar[RuleOperator] = RuleOperator.year_lte

    def _matches(self, item: AttributeData) -> bool:
        attribute_date = self.get_attribute_date(item)
        return (attribute_date <= self.cutoff) if attribute_date else False


@OperatorRegistry.register
class YearLT(DateYearOperator):
    rule_operator: ClassVar[RuleOperator] = RuleOperator.year_lt

    def _matches(self, item: AttributeData) -> bool:
        attribute_date = self.get_attribute_date(item)
        return (attribute_date < self.cutoff) if attribute_date else False


@OperatorRegistry.register
class YearGTE(DateYearOperator):
    rule_operator: ClassVar[RuleOperator] = RuleOperator.year_gte

    def _matches(self, item: AttributeData) -> bool:
        attribute_date = self.get_attribute_date(item)
        return (attribute_date >= self.cutoff) if attribute_date else False


@OperatorRegistry.register
class YearGT(DateYearOperator):
    rule_operator: ClassVar[RuleOperator] = RuleOperator.year_gt

    def _matches(self, item: AttributeData) -> bool:
        attribute_date = self.get_attribute_date(item)
        return (attribute_date > self.cutoff) if attribute_date else False
