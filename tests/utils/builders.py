import random
import string


def random_str(length: int) -> str:
    return "".join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length))  # noqa: S311


def random_int(minimum: int = 1, maximum: int = 10) -> int:
    return random.randint(minimum, maximum)  # noqa: S311
