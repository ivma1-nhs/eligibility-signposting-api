import string
from collections.abc import Sequence
from datetime import date
from random import choice, randint, shuffle
from typing import Any, Literal

from faker import Faker
from faker.providers import BaseProvider


class PersonDetailProvider(BaseProvider):
    def icb(self) -> str | None:
        if randint(0, 3):
            return f"{choice(string.ascii_uppercase)}{choice(string.ascii_uppercase)}{choice(string.digits)}"
        return None

    def gp_practice(self) -> str | None:
        if randint(0, 3):
            return f"{choice(string.ascii_uppercase)}{randint(1, 99999):05}"
        return None

    def pcn(self) -> str | None:
        if randint(0, 3):
            return f"{choice(string.ascii_uppercase)}{randint(1, 99999):05}"
        return None

    def comissioning_region(self) -> str | None:
        if randint(0, 3):
            return f"{choice(string.ascii_uppercase)}{randint(1, 99):02}"
        return None

    def msoa(self) -> str | None:
        if randint(0, 3):
            return f"{choice(string.ascii_uppercase)}{randint(1, 99999999):08}"
        return None

    def lsoa(self) -> str | None:
        if randint(0, 3):
            return f"{choice(string.ascii_uppercase)}{randint(1, 99999999):08}"
        return None


def person_rows_builder(  # noqa:PLR0913
    nhs_number: str,
    *,
    date_of_birth: date | None = None,
    gender: Literal["0", "1"] | None = None,
    postcode: str | None = None,
    cohorts: Sequence[str] | None = None,
    vaccines: Sequence[str] | None = None,
    icb: str | None = None,
    gp_practice: str | None = None,
    pcn: str | None = None,
    comissioning_region: str | None = None,
    thirteen_q: bool | None = None,
    care_home: bool | None = None,
    de: bool | None = None,
    msoa: str | None = None,
    lsoa: str | None = None,
) -> list[dict[str, Any]]:
    faker = Faker("en_UK")
    faker.add_provider(PersonDetailProvider)

    key = f"PERSON#{nhs_number}"
    date_of_birth = date_of_birth or faker.date_of_birth(minimum_age=18, maximum_age=99)
    gender = gender or choice(("0", "1"))
    postcode = postcode or faker.postcode()
    cohorts = cohorts if cohorts is not None else ["cohort-a", "cohort-b"]
    vaccines = vaccines if vaccines is not None else ["RSV", "COVID"]
    icb = icb or faker.icb()
    gp_practice = gp_practice or faker.gp_practice()
    pcn = pcn or faker.pcn()
    comissioning_region = comissioning_region or faker.comissioning_region()
    thirteen_q = thirteen_q if thirteen_q is not None else faker.boolean()
    care_home = care_home if care_home is not None else faker.boolean()
    de = de if de is not None else faker.boolean()
    msoa = msoa or faker.msoa()
    lsoa = lsoa or faker.lsoa()
    rows: list[dict[str, Any]] = [
        {
            "NHS_NUMBER": key,
            "ATTRIBUTE_TYPE": "PERSON",
            "DATE_OF_BIRTH": date_of_birth.strftime("%Y%m%d"),
            "GENDER": gender,
            "POSTCODE": postcode,
            "ICB": icb,
            "GP_PRACTICE": gp_practice,
            "PCN": pcn,
            "COMISSIONING_REGION": comissioning_region,
            "13Q_FLAG": "Y" if thirteen_q else "N",
            "CARE_HOME_FLAG": "Y" if care_home else "N",
            "DE_FLAG": "Y" if de else "N",
            "MSOA": msoa,
            "LSOA": lsoa,
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

    shuffle(rows)
    return rows
