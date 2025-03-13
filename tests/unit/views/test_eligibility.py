import logging
from http import HTTPStatus

from brunns.matchers.data import json_matching as is_json_that
from brunns.matchers.werkzeug import is_werkzeug_response as is_response
from flask.testing import FlaskClient
from hamcrest import assert_that, empty, is_

logger = logging.getLogger(__name__)


def test_nhs_number_given(client: FlaskClient):
    # Given

    # When
    response = client.get("/eligibility/12345")

    # Then
    assert_that(response, is_response().with_status_code(HTTPStatus.OK).and_text(is_json_that(is_(empty()))))


def test_no_nhs_number_given(client: FlaskClient):
    # Given

    # When
    response = client.get("/eligibility/")

    # Then
    assert_that(response, is_response().with_status_code(HTTPStatus.NOT_FOUND))
