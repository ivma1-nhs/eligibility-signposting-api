from collections.abc import Generator
from datetime import date
from typing import Any

import pytest
from faker import Faker
from hamcrest import assert_that, has_entries

from eligibility_signposting_api.model.eligibility import NHSNumber
from eligibility_signposting_api.repos.eligibility_repo import EligibilityRepo

FAKER = Faker()


@pytest.fixture(scope="module")
def persisted_person(eligibility_table: Any) -> Generator[tuple[NHSNumber, date]]:
    nhs_number = NHSNumber(f"5{FAKER.random_int(max=999999999):09d}")
    date_of_birth = FAKER.date_of_birth()
    eligibility_table.put_item(
        Item={
            "NHS_NUMBER": f"PERSON#{nhs_number}",
            "ATTRIBUTE_TYPE": f"PERSON#{nhs_number}",
            "DATE_OF_BIRTH": date_of_birth.strftime("%Y%m%d"),
        }
    )
    yield nhs_number, date_of_birth
    eligibility_table.delete_item(Key={"NHS_NUMBER": f"PERSON#{nhs_number}", "ATTRIBUTE_TYPE": f"PERSON#{nhs_number}"})


def test_person_found(eligibility_table: Any, persisted_person: tuple[NHSNumber, date]):
    # Given
    nhs_number, date_of_birth = persisted_person
    repo = EligibilityRepo(eligibility_table)

    # When
    actual = repo.get_person(nhs_number)

    # Then
    assert_that(
        actual,
        has_entries(
            {
                "NHS_NUMBER": f"PERSON#{nhs_number}",
                "ATTRIBUTE_TYPE": f"PERSON#{nhs_number}",
                "DATE_OF_BIRTH": date_of_birth.strftime("%Y%m%d"),
            }
        ),
    )
