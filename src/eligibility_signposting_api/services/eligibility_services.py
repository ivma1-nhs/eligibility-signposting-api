import logging

from wireup import service

from eligibility_signposting_api.model.eligibility import EligibilityStatus, NHSNumber
from eligibility_signposting_api.repos import EligibilityRepo, NotFoundError, RulesRepo

logger = logging.getLogger(__name__)


class UnknownPersonError(Exception):
    pass


@service
class EligibilityService:
    def __init__(self, eligibility_repo: EligibilityRepo, rules_repo: RulesRepo) -> None:
        super().__init__()
        self.eligibility_repo = eligibility_repo
        self.rules_repo = rules_repo

    def get_eligibility_status(self, nhs_number: NHSNumber | None = None) -> EligibilityStatus:
        if nhs_number:
            try:
                person_data = self.eligibility_repo.get_eligibility_data(nhs_number)
                campaign_configs = list(self.rules_repo.get_campaign_configs())
                logger.debug(
                    "got person_data %r",
                    person_data,
                    extra={
                        "campaign_configs": [c.model_dump(by_alias=True) for c in campaign_configs],
                        "person_data": person_data,
                        "nhs_number": nhs_number,
                    },
                )
            except NotFoundError as e:
                raise UnknownPersonError from e
            else:
                # TODO: Apply rules here  # noqa: TD002, TD003, FIX002
                logger.debug(
                    "Assessing eligibility for %s with %s",
                    person_data,
                    campaign_configs,
                    extra={
                        "campaign_configs": [c.model_dump(by_alias=True) for c in campaign_configs],
                        "person_data": person_data,
                        "nhs_number": nhs_number,
                    },
                )
                return EligibilityStatus(eligible=True, reasons=[], actions=[])

        raise UnknownPersonError
