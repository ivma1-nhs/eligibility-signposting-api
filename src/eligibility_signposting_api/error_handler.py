import logging
import traceback
from http import HTTPStatus

from fhir.resources.operationoutcome import OperationOutcome, OperationOutcomeIssue
from flask import make_response
from flask.typing import ResponseReturnValue
from werkzeug.exceptions import HTTPException

logger = logging.getLogger(__name__)


def handle_exception(e: Exception) -> ResponseReturnValue | HTTPException:
    logger.exception("Unexpected Exception", exc_info=e)

    # Let Flask handle its own exceptions for now.
    if isinstance(e, HTTPException):
        return e

    problem = OperationOutcome(
        issue=[
            OperationOutcomeIssue(
                severity="severe", code="unexpected", diagnostics="".join(traceback.format_exception(e))
            )  # pyright: ignore[reportCallIssue]
        ]
    )
    return make_response(problem.model_dump(), HTTPStatus.INTERNAL_SERVER_ERROR)
