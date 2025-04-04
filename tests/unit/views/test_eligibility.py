import logging
from http import HTTPStatus

from brunns.matchers.data import json_matching as is_json_that
from brunns.matchers.werkzeug import is_werkzeug_response as is_response
from flask import Flask
from flask.testing import FlaskClient
from hamcrest import assert_that, has_entries
from wireup.integration.flask import get_app_container

from eligibility_signposting_api.model.eligibility import Eligibility, NHSNumber
from eligibility_signposting_api.services import EligibilityService, UnknownPersonError

logger = logging.getLogger(__name__)


class FakeEligibilityService(EligibilityService):
    def __init__(self):
        pass

    def get_eligibility(self, _: NHSNumber | None = None) -> Eligibility:
        return Eligibility(processed_suggestions=[])


class FakeUnknownPersonEligibilityService(EligibilityService):
    def __init__(self):
        pass

    def get_eligibility(self, _: NHSNumber | None = None) -> Eligibility:
        raise UnknownPersonError


class FakeUnexpectedErrorEligibilityService(EligibilityService):
    def __init__(self):
        pass

    def get_eligibility(self, _: NHSNumber | None = None) -> Eligibility:
        raise ValueError


def test_nhs_number_given(app: Flask, client: FlaskClient):
    # Given
    with get_app_container(app).override.service(EligibilityService, new=FakeEligibilityService()):
        # When
        response = client.get("/eligibility/?nhs_number=12345")

        # Then
    assert_that(
        response,
        is_response().with_status_code(HTTPStatus.OK).and_text(is_json_that(has_entries(processed_suggestions=[]))),
    )


def test_no_nhs_number_given(app: Flask, client: FlaskClient):
    # Given
    with get_app_container(app).override.service(EligibilityService, new=FakeUnknownPersonEligibilityService()):
        # When
        response = client.get("/eligibility/")

    # Then
    assert_that(response, is_response().with_status_code(HTTPStatus.NOT_FOUND))


def test_unexpected_error(app: Flask, client: FlaskClient):
    # Given
    with get_app_container(app).override.service(EligibilityService, new=FakeUnexpectedErrorEligibilityService()):
        response = client.get("/eligibility/?nhs_number=12345")
        assert_that(response, is_response().with_status_code(HTTPStatus.INTERNAL_SERVER_ERROR))
