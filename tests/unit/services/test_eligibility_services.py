from unittest.mock import MagicMock

import pytest

from eligibility_signposting_api.model.eligibility import Eligibility, NHSNumber
from eligibility_signposting_api.repos import EligibilityRepo, NotFoundError
from eligibility_signposting_api.services import EligibilityService, UnknownPersonError


def test_eligibility_service_returns_from_repo():
    # Given
    eligibility_repo = MagicMock(spec=EligibilityRepo)
    eligibility_repo.get_eligibility = MagicMock(return_value=[])
    ps = EligibilityService(eligibility_repo)

    # When
    actual = ps.get_eligibility(NHSNumber("1234567890"))

    # Then
    assert actual == Eligibility(processed_suggestions=[])


def test_eligibility_service_for_nonexistent_name():
    # Given
    eligibility_repo = MagicMock(spec=EligibilityRepo)
    eligibility_repo.get_eligibility_data = MagicMock(side_effect=NotFoundError)
    ps = EligibilityService(eligibility_repo)

    # When
    with pytest.raises(UnknownPersonError):
        ps.get_eligibility(NHSNumber("1234567890"))
