from collections.abc import Generator
from typing import Any

import pytest
from faker import Faker
from hamcrest import assert_that, contains_inanyorder

from eligibility_signposting_api.model.eligibility import DateOfBirth, NHSNumber, Postcode
from eligibility_signposting_api.repos import NotFoundError
from eligibility_signposting_api.repos.eligibility_repo import EligibilityRepo


@pytest.fixture(scope="module")
def persisted_person(eligibility_table: Any, faker: Faker) -> Generator[tuple[NHSNumber, DateOfBirth, Postcode]]:
    nhs_number = NHSNumber(f"5{faker.random_int(max=999999999):09d}")
    date_of_birth = DateOfBirth(faker.date_of_birth())
    postcode = Postcode(faker.postcode())
    eligibility_table.put_item(
        Item={
            "NHS_NUMBER": f"PERSON#{nhs_number}",
            "ATTRIBUTE_TYPE": f"PERSON#{nhs_number}",
            "DATE_OF_BIRTH": date_of_birth.strftime("%Y%m%d"),
            "POSTCODE": postcode,
        }
    )
    eligibility_table.put_item(
        Item={"NHS_NUMBER": f"PERSON#{nhs_number}", "ATTRIBUTE_TYPE": "COHORTS", "COHORT_MAP": {}}
    )
    yield nhs_number, date_of_birth, postcode
    eligibility_table.delete_item(Key={"NHS_NUMBER": f"PERSON#{nhs_number}", "ATTRIBUTE_TYPE": f"PERSON#{nhs_number}"})
    eligibility_table.delete_item(Key={"NHS_NUMBER": f"PERSON#{nhs_number}", "ATTRIBUTE_TYPE": "COHORTS"})


def test_person_found(eligibility_table: Any, persisted_person: tuple[NHSNumber, DateOfBirth, Postcode]):
    # Given
    nhs_number, date_of_birth, postcode = persisted_person
    repo = EligibilityRepo(eligibility_table)

    # When
    actual = repo.get_person(nhs_number)

    # Then
    assert_that(
        actual,
        contains_inanyorder(
            {
                "NHS_NUMBER": f"PERSON#{nhs_number}",
                "ATTRIBUTE_TYPE": f"PERSON#{nhs_number}",
                "DATE_OF_BIRTH": date_of_birth.strftime("%Y%m%d"),
                "POSTCODE": postcode,
            },
            {"NHS_NUMBER": f"PERSON#{nhs_number}", "ATTRIBUTE_TYPE": "COHORTS", "COHORT_MAP": {}},
        ),
    )


def test_person_not_found(eligibility_table: Any, faker: Faker):
    # Given
    nhs_number = NHSNumber(f"5{faker.random_int(max=999999999):09d}")
    repo = EligibilityRepo(eligibility_table)

    # When, Then
    with pytest.raises(NotFoundError):
        repo.get_person(nhs_number)
