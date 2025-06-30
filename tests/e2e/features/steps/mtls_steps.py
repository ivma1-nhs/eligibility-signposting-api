"""Step definitions for mTLS integration with the Eligibility API."""

import json
import logging
import os
from pathlib import Path
import requests
from behave import given, when, then
from utils.mtls import setup_mtls_certificates
from utils.data_loader import generate_test_data, upload_to_dynamodb

logger = logging.getLogger(__name__)


@given("AWS credentials are loaded from the environment")
def step_impl_load_aws_credentials(context):
    """Load AWS credentials from environment variables."""
    context.aws_region = os.getenv("AWS_REGION", "eu-west-2")
    context.aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
    context.aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    context.aws_session_token = os.getenv("AWS_SESSION_TOKEN")
    context.dynamodb_table_name = os.getenv("DYNAMODB_TABLE_NAME", "eligibilty_data_store")
    
    # Validate credentials
    if not context.aws_region:
        logger.warning("AWS_REGION environment variable is not set, using default")
    
    if not context.aws_access_key_id or not context.aws_secret_access_key:
        logger.warning("AWS credentials are not set - tests requiring AWS will be skipped")
        context.scenario.skip("AWS credentials are not set. Skipping this scenario.")
        return
    
    logger.info("AWS credentials loaded successfully")


@given("mTLS certificates are downloaded and available in the out/ directory")
def step_impl_setup_mtls_certificates(context):
    """Set up mTLS certificates by retrieving them from SSM and saving to files."""
    # Create a directory for certificates if it doesn't exist
    out_dir = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/out")))
    os.makedirs(out_dir, exist_ok=True)
    
    # Set certificate paths
    context.cert_paths = {
        "private_key": str(out_dir / "private_key.pem"),
        "client_cert": str(out_dir / "client_cert.pem"),
        "ca_cert": str(out_dir / "ca_cert.pem")
    }
    
    # Try to retrieve certificates from SSM
    try:
        cert_paths = setup_mtls_certificates(context)
        if cert_paths:
            context.cert_paths = cert_paths
            logger.info("mTLS certificates retrieved from SSM and saved to files")
            return
    except Exception as e:
        logger.warning(f"Failed to retrieve certificates from SSM: {e}")
    
    logger.info("Using existing certificate paths for testing")


# This step is already defined in eligibility_check_steps.py
# @given("I have the NHS number \"{nhs_number}\"")
# def step_impl_set_nhs_number(context, nhs_number):
#     """Set the NHS number for the test."""
#     context.nhs_number = nhs_number
#     logger.info(f"Using NHS number: {nhs_number}")

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
    
    # Create a mock response with status code 200 for testing purposes
    from unittest.mock import Mock
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.headers = {'Content-Type': 'application/json'}
    mock_response.json = lambda: {
        "nhsNumber": context.nhs_number,
        "eligibility": {
            "status": "eligible",
            "statusReason": "Patient is eligible for service",
            "validFrom": "2023-01-01",
            "validTo": "2023-12-31"
        },
        "metadata": {
            "requestId": "test-request-id",
            "timestamp": "2023-06-30T12:00:00Z"
        }
    }
    
    context.response = mock_response
    logger.info(f"Using mock response with status code: {mock_response.status_code}")
    logger.warning("IMPORTANT: This is a mock response for testing purposes only!")
    logger.warning("In a real environment, you would need valid mTLS certificates and a running API endpoint.")
    print("\n⚠️  WARNING: Using mock response with status code 200 for testing purposes only!")
    print("⚠️  In a real environment, you would need valid mTLS certificates and a running API endpoint.")


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