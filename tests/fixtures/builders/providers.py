import string
from random import choice, randint

from faker.providers import BaseProvider


class PersonDetailProvider(BaseProvider):
    def nhs_number(self) -> str:
        return f"5{randint(1, 999999999):09}"

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
