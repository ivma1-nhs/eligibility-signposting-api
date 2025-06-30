"""mTLS utility module for handling certificate management."""

import os
import logging
from pathlib import Path
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

# Certificate parameter names in SSM
PRIVATE_KEY_CERT_PARAM = "/test/mtls/api_private_key_cert"
CLIENT_CERT_PARAM = "/test/mtls/api_client_cert"
CA_CERT_PARAM = "/test/mtls/api_ca_cert"

# Certificate file names
PRIVATE_KEY_FILE = "api_private_key_cert.pem"
CLIENT_CERT_FILE = "api_client_cert.pem"
CA_CERT_FILE = "api_ca_cert.pem"


def get_ssm_parameter(
    param_name: str,
    with_decryption: bool = True,
    region_name: str = None,
    aws_access_key_id: str = None,
    aws_secret_access_key: str = None,
    aws_session_token: str = None,
) -> str:
    """Retrieve a parameter from AWS SSM Parameter Store.

    Args:
        param_name: Name of the parameter to retrieve
        with_decryption: Whether to decrypt the parameter value
        region_name: AWS region name
        aws_access_key_id: AWS access key ID
        aws_secret_access_key: AWS secret access key
        aws_session_token: AWS session token

    Returns:
        The parameter value as a string

    Raises:
        ClientError: If the parameter cannot be retrieved
    """
    try:
        ssm_client = boto3.client(
            "ssm",
            region_name=region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token,
        )
        response = ssm_client.get_parameter(Name=param_name, WithDecryption=with_decryption)
        return response["Parameter"]["Value"]
    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code")
        if error_code == "ParameterNotFound":
            logger.error(f"Error: SSM parameter '{param_name}' not found.")
        elif error_code == "AccessDeniedException":
            logger.error(
                f"Error: Access denied to SSM parameter '{param_name}'. Check your IAM permissions or provided credentials."
            )
        else:
            logger.error(f"AWS Client Error: {e}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise


def setup_mtls_certificates(context):
    """Set up mTLS certificates by retrieving them from SSM and saving to files.

    Args:
        context: Behave context object containing AWS credentials

    Returns:
        dict: Dictionary containing paths to certificate files
    """
    # Always use tests/e2e/data/out as the cert storage directory
    out_dir = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/out")))
    os.makedirs(out_dir, exist_ok=True)

    private_key_path = out_dir / PRIVATE_KEY_FILE
    client_cert_path = out_dir / CLIENT_CERT_FILE
    ca_cert_path = out_dir / CA_CERT_FILE

    # Check if cert files exist, if not, fetch from SSM and create them
    if not (private_key_path.exists() and client_cert_path.exists() and ca_cert_path.exists()):
        logger.info("Certificate files not found. Fetching from SSM and creating them...")
        
        certs_to_retrieve = {
            "private_key": PRIVATE_KEY_CERT_PARAM,
            "client_cert": CLIENT_CERT_PARAM,
            "ca_cert": CA_CERT_PARAM
        }
        
        retrieved_certs_content = {}
        
        for cert_type, param_name in certs_to_retrieve.items():
            logger.info(f"Retrieving {cert_type.replace('_', ' ').title()} parameter: {param_name}...")
            try:
                cert_content = get_ssm_parameter(
                    param_name,
                    with_decryption=True,
                    region_name=context.aws_region,
                    aws_access_key_id=context.aws_access_key_id,
                    aws_secret_access_key=context.aws_secret_access_key,
                    aws_session_token=context.aws_session_token
                )
                retrieved_certs_content[cert_type] = cert_content
                logger.info(f"Successfully retrieved {cert_type.replace('_', ' ').title()}")
            except Exception as e:
                logger.error(f"Failed to retrieve {cert_type} certificate: {e}")
                return None
        
        if not all(key in retrieved_certs_content for key in ["private_key", "client_cert", "ca_cert"]):
            logger.error("One or more required certificates could not be retrieved from SSM.")
            return None
        
        # Write certificates to files
        with open(private_key_path, "w") as f:
            f.write(retrieved_certs_content["private_key"])
        logger.info(f"Private key written to: {private_key_path}")
        
        with open(client_cert_path, "w") as f:
            f.write(retrieved_certs_content["client_cert"])
        logger.info(f"Client certificate written to: {client_cert_path}")
        
        with open(ca_cert_path, "w") as f:
            f.write(retrieved_certs_content["ca_cert"])
        logger.info(f"CA certificate written to: {ca_cert_path}")
    else:
        logger.info("Certificate files already exist, using existing files.")

    return {
        "private_key": str(private_key_path),
        "client_cert": str(client_cert_path),
        "ca_cert": str(ca_cert_path)
    }