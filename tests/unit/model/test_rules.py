import pytest
from dateutil.relativedelta import relativedelta
from faker import Faker

from tests.fixtures.builders.model.rule import IterationFactory, RawCampaignConfigFactory


def test_start_date_must_be_before_end_date(faker: Faker):
    # Given
    start_date = faker.date_object()
    end_date = start_date - relativedelta(days=1)

    # When, Then
    with pytest.raises(
        ValueError,
        match=r"1 validation error for CampaignConfig\n"
        r".*start date .* after end date",
    ):
        RawCampaignConfigFactory.build(start_date=start_date, end_date=end_date)


def test_iteration_with_overlapping_start_dates_not_allowed(faker: Faker):
    # Given
    start_date = faker.date_object()
    iteration1 = IterationFactory.build(iteration_date=start_date)
    iteration2 = IterationFactory.build(iteration_date=start_date)

    # When, Then
    with pytest.raises(
        ValueError,
        match=r"1 validation error for CampaignConfig\n"
        r".*2 iterations with iteration date",
    ):
        RawCampaignConfigFactory.build(start_date=start_date, iterations=[iteration1, iteration2])


def test_iteration_must_have_active_iteration_from_its_start(faker: Faker):
    # Given
    start_date = faker.date_object()
    iteration = IterationFactory.build(iteration_date=start_date + relativedelta(days=1))

    # When, Then
    with pytest.raises(
        ValueError,
        match=r"1 validation error for CampaignConfig\n"
        r".*1st iteration starts later",
    ):
        RawCampaignConfigFactory.build(start_date=start_date, iterations=[iteration])
