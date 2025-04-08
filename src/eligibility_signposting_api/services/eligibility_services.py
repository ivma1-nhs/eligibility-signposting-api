import logging

from wireup import service

from eligibility_signposting_api.model.eligibility import Eligibility, NHSNumber
from eligibility_signposting_api.repos import EligibilityRepo, NotFoundError

logger = logging.getLogger(__name__)


class UnknownPersonError(Exception):
    pass


@service
class EligibilityService:
    def __init__(self, eligibility_repo: EligibilityRepo) -> None:
        super().__init__()
        self.eligibility_repo = eligibility_repo

    def get_eligibility(self, nhs_number: NHSNumber | None = None) -> Eligibility:
        if nhs_number:
            try:
                eligibility_data = self.eligibility_repo.get_eligibility_data(nhs_number)
                logger.debug(
                    "got eligibility_data %r",
                    eligibility_data,
                    extra={"eligibility_data": eligibility_data, "nhs_number": nhs_number},
                )
            except NotFoundError as e:
                raise UnknownPersonError from e
            else:
                # TODO: Apply rules here  # noqa: TD002, TD003, FIX002
                return Eligibility(processed_suggestions=[])

        raise UnknownPersonError
