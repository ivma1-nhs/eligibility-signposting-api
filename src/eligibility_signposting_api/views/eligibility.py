import logging
from http import HTTPStatus

from fhir.resources.operationoutcome import OperationOutcome, OperationOutcomeIssue
from flask import Blueprint, make_response, request
from flask.typing import ResponseReturnValue
from wireup import Injected

from eligibility_signposting_api.model.eligibility import Eligibility, NHSNumber
from eligibility_signposting_api.services import EligibilityService, UnknownPersonError
from eligibility_signposting_api.views.response_models import EligibilityResponse

logger = logging.getLogger(__name__)

eligibility_blueprint = Blueprint("eligibility", __name__)


@eligibility_blueprint.get("/")
def check_eligibility(eligibility_service: Injected[EligibilityService]) -> ResponseReturnValue:
    nhs_number = NHSNumber(request.args.get("nhs_number", ""))
    logger.debug("checking nhs_number %r in %r", nhs_number, eligibility_service, extra={"nhs_number": nhs_number})
    try:
        eligibility = eligibility_service.get_eligibility(nhs_number)
    except UnknownPersonError:
        logger.debug("nhs_number %r not found", nhs_number, extra={"nhs_number": nhs_number})
        problem = OperationOutcome(
            issue=[
                OperationOutcomeIssue(
                    severity="information",
                    code="nhs-number-not-found",
                    diagnostics=f'NHS Number "{nhs_number}" not found.',
                )  # pyright: ignore[reportCallIssue]
            ]
        )
        return make_response(problem.model_dump(by_alias=True), HTTPStatus.NOT_FOUND)
    else:
        eligibility_response = build_eligibility_response(eligibility)
        return make_response(eligibility_response.model_dump(by_alias=True), HTTPStatus.OK)


def build_eligibility_response(eligibility: Eligibility) -> EligibilityResponse:
    return EligibilityResponse(processed_suggestions=eligibility.processed_suggestions)
