import pytest
from faker import Faker

from tests.fixtures.builders.model.rule import CampaignConfigFactory, IterationFactory


def test_iteration_with_overlapping_start_dates_not_allowed(faker: Faker):
    # Given
    iteration_date = faker.date("%Y%m%d")
    iteration1 = IterationFactory.build(iteration_date=iteration_date)
    iteration2 = IterationFactory.build(iteration_date=iteration_date)

    # When, Then
    with pytest.raises(
        ValueError,
        match=r"1 validation error for CampaignConfig\n"
        r".*2 iterations with iteration date",
    ):
        CampaignConfigFactory.build(iterations=[iteration1, iteration2])
