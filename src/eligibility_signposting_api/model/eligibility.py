from datetime import date
from typing import NewType

NHSNumber = NewType("NHSNumber", str)
DateOfBirth = NewType("DateOfBirth", date)
Postcode = NewType("Postcode", str)
