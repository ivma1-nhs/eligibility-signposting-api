import logging
from http import HTTPStatus

from fhir.resources.R4B.bundle import Bundle, BundleEntry
from fhir.resources.R4B.guidanceresponse import GuidanceResponse
from fhir.resources.R4B.location import Location
from fhir.resources.R4B.operationoutcome import OperationOutcome, OperationOutcomeIssue
from fhir.resources.R4B.requestgroup import RequestGroup
from fhir.resources.R4B.task import Task
from flask import Blueprint, make_response, request
from flask.typing import ResponseReturnValue
from wireup import Injected

from eligibility_signposting_api.model.eligibility import EligibilityStatus, NHSNumber
from eligibility_signposting_api.services import EligibilityService, UnknownPersonError

logger = logging.getLogger(__name__)

eligibility_blueprint = Blueprint("eligibility", __name__)


@eligibility_blueprint.get("/")
def check_eligibility(eligibility_service: Injected[EligibilityService]) -> ResponseReturnValue:
    nhs_number = NHSNumber(request.args.get("nhs_number", ""))
    logger.debug("checking nhs_number %r in %r", nhs_number, eligibility_service, extra={"nhs_number": nhs_number})
    try:
        eligibility_status = eligibility_service.get_eligibility_status(nhs_number)
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
        bundle = build_bundle(eligibility_status)
        return make_response(bundle.model_dump(by_alias=True), HTTPStatus.OK)


def build_bundle(_eligibility_status: EligibilityStatus) -> Bundle:
    return Bundle(  # pyright: ignore[reportCallIssue]
        id="dummy-bundle",
        type="collection",
        entry=[
            BundleEntry(  # pyright: ignore[reportCallIssue]
                resource=GuidanceResponse(id="dummy-guidance-response", status="requested", moduleCodeableConcept={})  # pyright: ignore[reportCallIssue]
            ),
            BundleEntry(resource=RequestGroup(id="dummy-request-group", intent="proposal", status="requested")),  # pyright: ignore[reportCallIssue]
            BundleEntry(resource=Task(id="dummy-task", intent="proposal", status="requested")),  # pyright: ignore[reportCallIssue]
            BundleEntry(resource=Location(id="dummy-location")),  # pyright: ignore[reportCallIssue]
        ],
    )
