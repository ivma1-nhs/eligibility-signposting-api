from datetime import date
from typing import NewType

from pydantic import BaseModel

NHSNumber = NewType("NHSNumber", str)
DateOfBirth = NewType("DateOfBirth", date)
Postcode = NewType("Postcode", str)


class Eligibility(BaseModel):
    processed_suggestions: list[dict]
