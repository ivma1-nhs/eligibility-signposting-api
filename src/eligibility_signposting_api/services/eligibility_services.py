import logging

from wireup import service

from eligibility_signposting_api.model import eligibility
from eligibility_signposting_api.repos import CampaignRepo, NotFoundError, PersonRepo
from eligibility_signposting_api.services.audit_service import AuditService
from eligibility_signposting_api.services.calculators import eligibility_calculator as calculator

logger = logging.getLogger(__name__)


class UnknownPersonError(Exception):
    pass


class InvalidQueryParamError(Exception):
    pass


@service
class EligibilityService:
    def __init__(
        self,
        person_repo: PersonRepo,
        campaign_repo: CampaignRepo,
        audit_service: AuditService,
        calculator_factory: calculator.EligibilityCalculatorFactory,
    ) -> None:
        super().__init__()
        self.person_repo = person_repo
        self.campaign_repo = campaign_repo
        self.audit_service = audit_service
        self.calculator_factory = calculator_factory

    def get_eligibility_status(
        self, nhs_number: eligibility.NHSNumber | None = None, *, include_actions_flag: bool = True
    ) -> eligibility.EligibilityStatus:
        """Calculate a person's eligibility for vaccination given an NHS number."""
        if nhs_number:
            try:
                person_data = self.person_repo.get_eligibility_data(nhs_number)
                campaign_configs = list(self.campaign_repo.get_campaign_configs())
                logger.debug(
                    "got person_data for %r",
                    nhs_number,
                    extra={
                        "campaign_configs": [c.model_dump(by_alias=True) for c in campaign_configs],
                        "person_data": person_data,
                        "nhs_number": nhs_number,
                    },
                )
            except NotFoundError as e:
                raise UnknownPersonError from e
            else:
                calc: calculator.EligibilityCalculator = self.calculator_factory.get(person_data, campaign_configs)
                self.audit_service.audit({"test_audit": "check if audit works"})
                return calc.evaluate_eligibility(include_actions_flag=include_actions_flag)

        raise UnknownPersonError  # pragma: no cover
