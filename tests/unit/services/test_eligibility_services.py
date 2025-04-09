from unittest.mock import MagicMock

import pytest
from brunns.matchers.object import true
from faker import Faker
from hamcrest import assert_that

from eligibility_signposting_api.model.eligibility import DateOfBirth, NHSNumber, Postcode
from eligibility_signposting_api.model.rules import RuleOperator, RuleType
from eligibility_signposting_api.repos import EligibilityRepo, NotFoundError, RulesRepo
from eligibility_signposting_api.services import EligibilityService, UnknownPersonError
from tests.utils.builders import CampaignConfigFactory, IterationFactory, IterationRuleFactory
from tests.utils.matchers.eligibility import is_eligibility_status


@pytest.fixture(scope="session")
def faker() -> Faker:
    return Faker("en_UK")


def test_eligibility_service_returns_from_repo():
    # Given
    eligibility_repo = MagicMock(spec=EligibilityRepo)
    rules_repo = MagicMock(spec=RulesRepo)
    eligibility_repo.get_eligibility = MagicMock(return_value=[])
    ps = EligibilityService(eligibility_repo, rules_repo)

    # When
    actual = ps.get_eligibility_status(NHSNumber("1234567890"))

    # Then
    assert_that(actual, is_eligibility_status().with_eligible(true()))


def test_eligibility_service_for_nonexistent_nhs_number():
    # Given
    eligibility_repo = MagicMock(spec=EligibilityRepo)
    rules_repo = MagicMock(spec=RulesRepo)
    eligibility_repo.get_eligibility_data = MagicMock(side_effect=NotFoundError)
    ps = EligibilityService(eligibility_repo, rules_repo)

    # When
    with pytest.raises(UnknownPersonError):
        ps.get_eligibility_status(NHSNumber("1234567890"))


def test_simple_rule(faker: Faker):
    # Given
    nhs_number = NHSNumber(f"5{faker.random_int(max=999999999):09d}")
    date_of_birth = DateOfBirth(faker.date_of_birth())
    postcode = Postcode(faker.postcode())

    eligibility_repo = MagicMock(spec=EligibilityRepo)
    rules_repo = MagicMock(spec=RulesRepo)
    eligibility_repo.get_eligibility = MagicMock(
        return_value=[
            {
                "NHS_NUMBER": f"PERSON#{nhs_number}",
                "ATTRIBUTE_TYPE": f"PERSON#{nhs_number}",
                "DATE_OF_BIRTH": date_of_birth.strftime("%Y%m%d"),
                "POSTCODE": postcode,
            }
        ]
    )
    rules_repo.get_campaign_config = MagicMock(
        return_value=CampaignConfigFactory.build(
            iterations=[
                IterationFactory.build(
                    iteration_rules=[IterationRuleFactory.build(type=RuleType.filter, operator=RuleOperator.gt)]
                )
            ]
        )
    )

    ps = EligibilityService(eligibility_repo, rules_repo)

    # When
    actual = ps.get_eligibility_status(NHSNumber(nhs_number))

    # Then
    assert_that(actual, is_eligibility_status().with_eligible(true()))
