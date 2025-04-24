import logging
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, date, datetime
from typing import ClassVar

from dateutil.relativedelta import relativedelta
from hamcrest.core.base_matcher import BaseMatcher

from eligibility_signposting_api.model.rules import RuleOperator

AttributeData = str | int | bool | None
logger = logging.getLogger(__name__)


@dataclass
class OperatorRule(BaseMatcher[AttributeData], ABC):
    rule_comparator: str

    @abstractmethod
    def _matches(self, item: AttributeData) -> bool: ...


class OperatorRegistry:
    registry: ClassVar[dict[RuleOperator, type[OperatorRule]]] = {}

    @staticmethod
    def register(rule_operator: RuleOperator) -> Callable[[type[OperatorRule]], type[OperatorRule]]:
        def decorator(the_type: type[OperatorRule]) -> type[OperatorRule]:
            OperatorRegistry.registry[rule_operator] = the_type
            return the_type

        return decorator

    @staticmethod
    def get(rule_operator: RuleOperator) -> type[OperatorRule]:
        if matcher_class := OperatorRegistry.registry.get(rule_operator):
            return matcher_class
        msg = f"{rule_operator} not implemented"
        raise NotImplementedError(msg)


@OperatorRegistry.register(RuleOperator.equals)
class Equals(OperatorRule):
    def _matches(self, item: AttributeData) -> bool:
        return item == self.rule_comparator


@OperatorRegistry.register(RuleOperator.gt)
class GT(OperatorRule):
    def _matches(self, item: AttributeData) -> bool:
        return bool(item) and int(item) > int(self.rule_comparator)


@OperatorRegistry.register(RuleOperator.lt)
class LT(OperatorRule):
    def _matches(self, item: AttributeData) -> bool:
        return bool(item) and int(item) < int(self.rule_comparator)


@OperatorRegistry.register(RuleOperator.ne)
class NE(OperatorRule):
    def _matches(self, item: AttributeData) -> bool:
        return bool(item) and item != self.rule_comparator


@OperatorRegistry.register(RuleOperator.gte)
class GTE(OperatorRule):
    def _matches(self, item: AttributeData) -> bool:
        return bool(item) and int(item) >= int(self.rule_comparator)


@OperatorRegistry.register(RuleOperator.lte)
class LTE(OperatorRule):
    def _matches(self, item: AttributeData) -> bool:
        return bool(item) and int(item) <= int(self.rule_comparator)


@OperatorRegistry.register(RuleOperator.contains)
class Contains(OperatorRule):
    def _matches(self, item: AttributeData) -> bool:
        return bool(item) and self.rule_comparator in str(item)


@OperatorRegistry.register(RuleOperator.not_contains)
class NotContains(OperatorRule):
    def _matches(self, item: AttributeData) -> bool:
        return self.rule_comparator not in str(item)


@OperatorRegistry.register(RuleOperator.starts_with)
class StartsWith(OperatorRule):
    def _matches(self, item: AttributeData) -> bool:
        return str(item).startswith(self.rule_comparator)


@OperatorRegistry.register(RuleOperator.not_starts_with)
class NotStartsWith(OperatorRule):
    def _matches(self, item: AttributeData) -> bool:
        return not str(item).startswith(self.rule_comparator)


@OperatorRegistry.register(RuleOperator.ends_with)
class EndsWith(OperatorRule):
    def _matches(self, item: AttributeData) -> bool:
        return str(item).endswith(self.rule_comparator)


@OperatorRegistry.register(RuleOperator.is_in)
class IsIn(OperatorRule):
    def _matches(self, item: AttributeData) -> bool:
        comparators = str(self.rule_comparator).split(",")
        return str(item) in comparators


@OperatorRegistry.register(RuleOperator.not_in)
class NotIn(OperatorRule):
    def _matches(self, item: AttributeData) -> bool:
        comparators = str(self.rule_comparator).split(",")
        return str(item) not in comparators


@OperatorRegistry.register(RuleOperator.member_of)
class MemberOf(OperatorRule):
    def _matches(self, item: AttributeData) -> bool:
        attribute_values = str(item).split(",")
        return self.rule_comparator in attribute_values


@OperatorRegistry.register(RuleOperator.not_member_of)
class NotMemberOf(OperatorRule):
    def _matches(self, item: AttributeData) -> bool:
        attribute_values = str(item).split(",")
        return self.rule_comparator not in attribute_values


@OperatorRegistry.register(RuleOperator.is_null)
class IsNull(OperatorRule):
    def _matches(self, item: AttributeData) -> bool:
        return item in (None, "")


@OperatorRegistry.register(RuleOperator.is_not_null)
class IsNotNull(OperatorRule):
    def _matches(self, item: AttributeData) -> bool:
        return item not in (None, "")


class RangeOperator(OperatorRule, ABC):
    def __init__(self, rule_comparator: str) -> None:
        super().__init__(rule_comparator=rule_comparator)
        low_comparator_str, high_comparator_str = str(self.rule_comparator).split(",")
        self.low_comparator = min(int(low_comparator_str), int(high_comparator_str))
        self.high_comparator = max(int(low_comparator_str), int(high_comparator_str))


@OperatorRegistry.register(RuleOperator.between)
class Between(RangeOperator):
    def _matches(self, item: AttributeData) -> bool:
        if item in (None, ""):
            return False
        return self.low_comparator <= int(item) <= self.high_comparator


@OperatorRegistry.register(RuleOperator.not_between)
class NotBetween(RangeOperator):
    def _matches(self, item: AttributeData) -> bool:
        if item in (None, ""):
            return False
        return not self.low_comparator <= int(item) <= self.high_comparator


@OperatorRegistry.register(RuleOperator.is_empty)
class IsEmpty(OperatorRule):
    def _matches(self, item: AttributeData) -> bool:
        return item is None or all(item.strip() == "" for item in str(item).split(","))


@OperatorRegistry.register(RuleOperator.is_not_empty)
class IsNotEmpty(OperatorRule):
    def _matches(self, item: AttributeData) -> bool:
        return item is not None and any(item.strip() != "" for item in str(item).split(","))


@OperatorRegistry.register(RuleOperator.is_true)
class IsTrue(OperatorRule):
    def _matches(self, item: AttributeData) -> bool:
        return item is True


@OperatorRegistry.register(RuleOperator.is_false)
class IsFalse(OperatorRule):
    def _matches(self, item: AttributeData) -> bool:
        return item is False


class DateOperator(OperatorRule, ABC):
    @property
    def today(self) -> date:
        return datetime.now(tz=UTC).date()

    @staticmethod
    def get_attribute_date(item: AttributeData) -> date | None:
        return datetime.strptime(str(item), "%Y%m%d").replace(tzinfo=UTC).date() if item else None


class DateDayOperator(DateOperator, ABC):
    @property
    def cutoff(self) -> date:
        return self.today + relativedelta(days=int(self.rule_comparator))


@OperatorRegistry.register(RuleOperator.day_lte)
class DayLTE(DateDayOperator):
    def _matches(self, item: AttributeData) -> bool:
        attribute_date = self.get_attribute_date(item)
        return (attribute_date <= self.cutoff) if attribute_date else False


@OperatorRegistry.register(RuleOperator.day_lt)
class DayLT(DateDayOperator):
    def _matches(self, item: AttributeData) -> bool:
        attribute_date = self.get_attribute_date(item)
        return (attribute_date < self.cutoff) if attribute_date else False


@OperatorRegistry.register(RuleOperator.day_gte)
class DayGTE(DateDayOperator):
    def _matches(self, item: AttributeData) -> bool:
        attribute_date = self.get_attribute_date(item)
        return (attribute_date >= self.cutoff) if attribute_date else False


@OperatorRegistry.register(RuleOperator.day_gt)
class DayGT(DateDayOperator):
    def _matches(self, item: AttributeData) -> bool:
        attribute_date = self.get_attribute_date(item)
        return (attribute_date > self.cutoff) if attribute_date else False


class DateWeekOperator(DateOperator, ABC):
    @property
    def cutoff(self) -> date:
        return self.today + relativedelta(weeks=int(self.rule_comparator))


@OperatorRegistry.register(RuleOperator.week_lte)
class WeekLTE(DateWeekOperator):
    def _matches(self, item: AttributeData) -> bool:
        attribute_date = self.get_attribute_date(item)
        return (attribute_date <= self.cutoff) if attribute_date else False


@OperatorRegistry.register(RuleOperator.week_lt)
class WeekLT(DateWeekOperator):
    def _matches(self, item: AttributeData) -> bool:
        attribute_date = self.get_attribute_date(item)
        return (attribute_date < self.cutoff) if attribute_date else False


@OperatorRegistry.register(RuleOperator.week_gte)
class WeekGTE(DateWeekOperator):
    def _matches(self, item: AttributeData) -> bool:
        attribute_date = self.get_attribute_date(item)
        return (attribute_date >= self.cutoff) if attribute_date else False


@OperatorRegistry.register(RuleOperator.week_gt)
class WeekGT(DateWeekOperator):
    def _matches(self, item: AttributeData) -> bool:
        attribute_date = self.get_attribute_date(item)
        return (attribute_date > self.cutoff) if attribute_date else False


class DateYearOperator(DateOperator, ABC):
    @property
    def cutoff(self) -> date:
        return self.today + relativedelta(years=int(self.rule_comparator))


@OperatorRegistry.register(RuleOperator.year_lte)
class YearLTE(DateYearOperator):
    def _matches(self, item: AttributeData) -> bool:
        attribute_date = self.get_attribute_date(item)
        return (attribute_date <= self.cutoff) if attribute_date else False


@OperatorRegistry.register(RuleOperator.year_lt)
class YearLT(DateYearOperator):
    def _matches(self, item: AttributeData) -> bool:
        attribute_date = self.get_attribute_date(item)
        return (attribute_date < self.cutoff) if attribute_date else False


@OperatorRegistry.register(RuleOperator.year_gte)
class YearGTE(DateYearOperator):
    def _matches(self, item: AttributeData) -> bool:
        attribute_date = self.get_attribute_date(item)
        return (attribute_date >= self.cutoff) if attribute_date else False


@OperatorRegistry.register(RuleOperator.year_gt)
class YearGT(DateYearOperator):
    def _matches(self, item: AttributeData) -> bool:
        attribute_date = self.get_attribute_date(item)
        return (attribute_date > self.cutoff) if attribute_date else False
