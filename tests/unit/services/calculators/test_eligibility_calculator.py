from faker import Faker
from hamcrest import assert_that, has_item

from eligibility_signposting_api.model.eligibility import ConditionName, NHSNumber, Status
from eligibility_signposting_api.services.calculators.eligibility_calculator import EligibilityCalculator
from tests.fixtures.builders.model import rule as rule_builder
from tests.fixtures.builders.repos.person import person_rows_builder
from tests.fixtures.matchers.eligibility import is_condition, is_eligibility_status


def test_not_base_eligible(faker: Faker):
    # Given
    nhs_number = NHSNumber(f"5{faker.random_int(max=999999999):09d}")

    person_rows = person_rows_builder(nhs_number, cohorts=["cohort1"])
    campaign_configs = [
        (
            rule_builder.CampaignConfigFactory.build(
                target="RSV",
                iterations=[
                    rule_builder.IterationFactory.build(
                        iteration_cohorts=[rule_builder.IterationCohortFactory.build(cohort_label="cohort2")]
                    )
                ],
            )
        )
    ]

    calculator = EligibilityCalculator(person_rows, campaign_configs)

    # When
    actual = calculator.evaluate_eligibility()

    # Then
    assert_that(
        actual,
        is_eligibility_status().with_conditions(
            has_item(is_condition().with_condition_name(ConditionName("RSV")).and_status(Status.not_eligible))
        ),
    )
