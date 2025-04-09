import random
import string

from polyfactory import Use
from polyfactory.factories.pydantic_factory import ModelFactory

from eligibility_signposting_api.model.rules import CampaignConfig, Iteration, IterationCohort, IterationRule


class IterationCohortFactory(ModelFactory[IterationCohort]):
    __model__ = IterationCohort


class IterationRuleFactory(ModelFactory[IterationRule]):
    __model__ = IterationRule


class IterationFactory(ModelFactory[Iteration]):
    __model__ = Iteration
    iteration_cohorts = Use(IterationCohortFactory.batch, size=2)
    iteration_rules = Use(IterationRuleFactory.batch, size=2)


class CampaignConfigFactory(ModelFactory[CampaignConfig]):
    __model__ = CampaignConfig
    iterations = Use(IterationFactory.batch, size=2)


def random_str(length: int) -> str:
    return "".join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length))  # noqa: S311
