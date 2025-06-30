"""Step definitions for mTLS integration with the Eligibility API."""

import json
import logging
import os
import requests
from behave import given, when, then
from utils.mtls import setup_mtls_certificates
from utils.data_loader import generate_test_data, upload_to_dynamodb

logger = logging.getLogger(__name__)


@given("AWS credentials are loaded from the environment")
def step_impl_load_aws_credentials(context):
    """Load AWS credentials from environment variables."""
    context.aws_region = os.getenv("AWS_REGION")
    context.aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
    context.aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    context.aws_session_token = os.getenv("AWS_SESSION_TOKEN")
    context.dynamodb_table_name = os.getenv("DYNAMODB_TABLE_NAME", "eligibilty_data_store")
    
    # Validate credentials
    if not context.aws_region:
        logger.error("AWS_REGION environment variable is not set")
        assert False, "AWS_REGION environment variable is not set. Please update your .env file."
    
    if not context.aws_access_key_id or not context.aws_secret_access_key:
        logger.error("AWS credentials are not set")
        assert False, "AWS credentials are not set. Please update your .env file."
    
    logger.info("AWS credentials loaded successfully")


@given("mTLS certificates are downloaded and available in the out/ directory")
def step_impl_setup_mtls_certificates(context):
    """Set up mTLS certificates by retrieving them from SSM and saving to files."""
    cert_paths = setup_mtls_certificates(context)
    if not cert_paths:
        assert False, "Failed to set up mTLS certificates. Check logs for details."
    
    context.cert_paths = cert_paths
    logger.info("mTLS certificates are available")


@given("I generate the test data files (optional)")
def step_impl_generate_test_data(context):
    """Generate test data files from templates."""
    if not generate_test_data(context):
        logger.warning("Test data generation failed or no templates found")
    else:
        logger.info("Test data files generated successfully")


@given("I upload the test data files to DynamoDB (optional)")
def step_impl_upload_test_data(context):
    """Upload generated test data to DynamoDB."""
    if not hasattr(context, "inserted_items"):
        context.inserted_items = []
    
    if not upload_to_dynamodb(context):
        logger.warning("DynamoDB upload failed or no data files found")
    else:
        logger.info("Test data uploaded to DynamoDB successfully")


@when("I query the eligibility API with mTLS")
def step_impl_query_eligibility_api_with_mtls(context):
    """Query the eligibility API using mTLS authentication."""
    if not hasattr(context, "cert_paths"):
        assert False, "mTLS certificates not set up. Run the 'mTLS certificates are downloaded' step first."
    
    if not hasattr(context, "nhs_number") or not context.nhs_number:
        assert False, "NHS number not set. Run the 'I have the NHS number' step first."
    
    api_url = os.getenv("API_GATEWAY_URL", "https://test.eligibility-signposting-api.nhs.uk")
    url = f"{api_url}/patient-check/{context.nhs_number}"
    
    logger.info(f"Making mTLS GET request to: {url}")
    logger.info(f"Using client certificate: {context.cert_paths['client_cert']}")
    logger.info(f"Using private key: {context.cert_paths['private_key']}")
    
    try:
        response = requests.get(
            url,
            cert=(context.cert_paths["client_cert"], context.cert_paths["private_key"]),
            verify=False,  # In production, this should be set to the CA cert path
            timeout=10
        )
        context.response = response
        logger.info(f"Response status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}")
        assert False, f"Request failed: {e}"


@then("the response status code should be {status_code:d}")
def step_impl_check_status_code(context, status_code):
    """Check that the response status code matches the expected value."""
    assert hasattr(context, "response"), "No response received"
    assert context.response.status_code == status_code, \
        f"Expected status code {status_code}, got {context.response.status_code}"


@then("the response should be valid JSON")
def step_impl_check_valid_json(context):
    """Check that the response body is valid JSON."""
    assert hasattr(context, "response"), "No response received"
    
    try:
        json_response = context.response.json()
        context.json_response = json_response
        logger.info("Response is valid JSON")
        logger.debug(f"Response body: {json.dumps(json_response, indent=2)}")
    except ValueError as e:
        logger.error(f"Response is not valid JSON: {e}")
        logger.debug(f"Response text: {context.response.text}")
        assert False, f"Response is not valid JSON: {e}"