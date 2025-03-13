import logging
from http import HTTPStatus

from flask import Blueprint, make_response
from flask.typing import ResponseReturnValue

from eligibility_signposting_api.model.eligibility import NHSNumber

logger = logging.getLogger(__name__)

eligibility = Blueprint("eligibility", __name__)


@eligibility.get("/<nhs_number>")
def check_eligibility(nhs_number: NHSNumber) -> ResponseReturnValue:
    logger.info("nhs_number: %s", nhs_number)
    return make_response({}, HTTPStatus.OK)
