import logging
import traceback
from http import HTTPStatus

from flask import make_response
from flask.typing import ResponseReturnValue
from werkzeug.exceptions import HTTPException

from eligibility_signposting_api.views.response_models import Problem

logger = logging.getLogger(__name__)


def handle_exception(e: Exception) -> ResponseReturnValue | HTTPException:
    logger.exception("Unexpected Exception", exc_info=e)

    # Let Flask handle its own exceptions for now.
    if isinstance(e, HTTPException):
        return e

    problem = Problem(
        title="Unexpected Exception",
        type=str(type(e)),
        status=HTTPStatus.INTERNAL_SERVER_ERROR,
        detail="".join(traceback.format_exception(e)),
    )
    return make_response(problem.model_dump(), HTTPStatus.INTERNAL_SERVER_ERROR)
