import string
from collections.abc import Sequence
from datetime import date
from random import choice, randint
from typing import Any

from faker import Faker
from faker.providers import BaseProvider


class IcbProvider(BaseProvider):
    def icb(self) -> str | None:
        if randint(0, 3):
            return f"{choice(string.ascii_uppercase)}{choice(string.ascii_uppercase)}{choice(string.digits)}"

        return None


def person_rows_builder(  # noqa:PLR0913
    nhs_number: str,
    *,
    date_of_birth: date | None = None,
    postcode: str | None = None,
    cohorts: Sequence[str] | None = None,
    vaccines: Sequence[str] | None = None,
    icb: str | None = None,
) -> list[dict[str, Any]]:
    faker = Faker("en_UK")
    faker.add_provider(IcbProvider)

    key = f"PERSON#{nhs_number}"
    date_of_birth = date_of_birth or faker.date_of_birth(minimum_age=18, maximum_age=99)
    postcode = postcode or faker.postcode()
    cohorts = cohorts if cohorts is not None else ["cohort-a", "cohort-b"]
    vaccines = vaccines if vaccines is not None else ["RSV", "COVID"]
    icb = icb or faker.icb()
    rows: list[dict[str, Any]] = [
        {
            "NHS_NUMBER": key,
            "ATTRIBUTE_TYPE": "PERSON",
            "DATE_OF_BIRTH": date_of_birth.strftime("%Y%m%d"),
            "POSTCODE": postcode,
            "ICB": icb,
        },
        {
            "NHS_NUMBER": key,
            "ATTRIBUTE_TYPE": "COHORTS",
            "COHORT_MAP": {
                "cohorts": {
                    "M": {
                        cohort: {"M": {"dateJoined": {"S": faker.past_date().strftime("%Y%m%d")}}} for cohort in cohorts
                    }
                }
            },
        },
    ]
    rows.extend(
        {
            "NHS_NUMBER": key,
            "ATTRIBUTE_TYPE": vaccine,
            "LAST_SUCCESSFUL_DATE": faker.past_date().strftime("%Y%m%d"),
            "OPTOUT": choice(["Y", "N"]),
            "LAST_INVITE_DATE": faker.past_date().strftime("%Y%m%d"),
        }
        for vaccine in vaccines
    )

    return rows
