from datetime import date
from typing import NewType

from pydantic import BaseModel

NHSNumber = NewType("NHSNumber", str)
DateOfBirth = NewType("DateOfBirth", date)
Postcode = NewType("Postcode", str)


class EligibilityStatus(BaseModel):
    eligible: bool
    reasons: list[dict]
    actions: list[dict]
