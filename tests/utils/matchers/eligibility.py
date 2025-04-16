from hamcrest.core.matcher import Matcher

from eligibility_signposting_api.model.eligibility import EligibilityStatus

from .meta import BaseAutoMatcher


class EligibilityStatusMatcher(BaseAutoMatcher[EligibilityStatus]): ...


def is_eligibility_status() -> Matcher[EligibilityStatus]:
    return EligibilityStatusMatcher()
