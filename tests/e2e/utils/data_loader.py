"""Data loader utility module for generating and loading test data."""

import json
import logging
import os
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import boto3
from botocore.exceptions import BotoCoreError, ClientError

logger = logging.getLogger(__name__)

# Constants
DATE_FORMAT = "%Y%m%d"
VAR_PATTERN = re.compile(r"<<([^<>]+)>>")
REQUIRED_TOKEN_PARTS = 3


class DateVariableResolver:
    """Resolver for date variables in test data templates."""

    def __init__(self, today: datetime = None):
        """Initialize the resolver with the current date or a specified date.

        Args:
            today: Date to use as "today". Defaults to current UTC date.
        """
        self.today = today or datetime.now(tz=timezone.UTC)

    def resolve(self, token: str) -> str:
        """Resolve a date variable token to a date string.

        Args:
            token: Token to resolve, e.g. "DATE_day_1" for tomorrow

        Returns:
            Resolved date string in format YYYYMMDD

        Raises:
            ValueError: If the token format is invalid or unsupported
        """
        logger.debug("Resolving variable: %s", token)
        parts = token.split("_")
        if len(parts) < REQUIRED_TOKEN_PARTS or parts[0].upper() != "DATE":
            msg = f"Unsupported variable format: {token}"
            raise ValueError(msg)
        
        _, unit, value = parts[0], parts[1].lower(), parts[2]
        try:
            offset = int(value)
        except ValueError as err:
            msg = f"Invalid offset value: {value}"
            raise ValueError(msg) from err
        
        if unit == "day":
            return (self.today + timedelta(days=offset)).strftime(DATE_FORMAT)
        if unit == "week":
            return (self.today + timedelta(weeks=offset)).strftime(DATE_FORMAT)
        if unit == "year":
            return (self.today.replace(year=self.today.year + offset)).strftime(DATE_FORMAT)
        if unit == "age":
            try:
                birth_date = self.today.replace(year=self.today.year - offset)
            except ValueError:
                birth_date = self.today.replace(month=2, day=28, year=self.today.year - offset)
            return birth_date.strftime(DATE_FORMAT)
        
        msg = f"Unsupported calculation unit: {unit}"
        raise ValueError(msg)


class JsonTestDataProcessor:
    """Processor for JSON test data templates."""

    def __init__(self, input_dir: Path, output_dir: Path, resolver: DateVariableResolver):
        """Initialize the processor with input/output directories and a variable resolver.

        Args:
            input_dir: Directory containing template JSON files
            output_dir: Directory to write processed JSON files
            resolver: Variable resolver to use for processing templates
        """
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.resolver = resolver

    def resolve_placeholders(self, obj: Any) -> Any:
        """Recursively resolve placeholders in an object.

        Args:
            obj: Object to process (dict, list, string, or other)

        Returns:
            Processed object with resolved placeholders
        """
        if isinstance(obj, dict):
            return {k: self.resolve_placeholders(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [self.resolve_placeholders(item) for item in obj]
        if isinstance(obj, str):
            return VAR_PATTERN.sub(self._replace_token, obj)
        return obj

    def _replace_token(self, match: re.Match) -> str:
        """Replace a matched token with its resolved value.

        Args:
            match: Regex match object containing the token

        Returns:
            Resolved value or the original token if resolution fails
        """
        token = match.group(1)
        try:
            return self.resolver.resolve(token)
        except ValueError:
            logger.warning("Failed to resolve variable: %s", token)
            return match.group(0)

    def process_file(self, file_path: Path) -> bool:
        """Process a single JSON template file.

        Args:
            file_path: Path to the template file

        Returns:
            True if processing was successful, False otherwise
        """
        logger.info("Processing file: %s", file_path)
        try:
            with file_path.open() as f:
                content = json.load(f)
        except Exception:
            logger.exception("Failed to read file: %s", file_path)
            return False
        
        try:
            resolved = self.resolve_placeholders(content)
        except Exception:
            logger.exception("Failed to resolve placeholders in file: %s", file_path)
            return False
        
        if "data" not in resolved:
            logger.error("Missing 'data' key in file: %s", file_path)
            return False
        
        relative_path = file_path.relative_to(self.input_dir)
        output_path = self.output_dir / relative_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with output_path.open("w") as f:
                json.dump(resolved["data"], f, indent=2)
            logger.info("Written resolved file: %s", output_path)
            return True
        except Exception:
            logger.exception("Failed to write output to: %s", output_path)
            return False


def generate_test_data(context) -> bool:
    """Generate test data files from templates.

    Args:
        context: Behave context object

    Returns:
        True if data generation was successful, False otherwise
    """
    input_dir = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "../data")))
    output_dir = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/out")))
    output_dir.mkdir(parents=True, exist_ok=True)
    
    resolver = DateVariableResolver()
    processor = JsonTestDataProcessor(input_dir, output_dir, resolver)
    
    logger.info("Scanning for JSON files in directory: %s", input_dir)
    success = True
    file_count = 0
    
    for root, _, files in os.walk(input_dir):
        for file in files:
            file_path = Path(root) / file
            if file.endswith(".json") and "out" not in str(file_path):
                file_count += 1
                if not processor.process_file(file_path):
                    success = False
            else:
                logger.debug("Skipping file: %s", file)
    
    if file_count == 0:
        logger.warning("No JSON template files found in %s", input_dir)
        return False
    
    logger.info("Processed %d JSON files", file_count)
    return success


def upload_to_dynamodb(context) -> bool:
    """Upload generated test data to DynamoDB.

    Args:
        context: Behave context object containing AWS credentials and configuration

    Returns:
        True if upload was successful, False otherwise
    """
    try:
        # Connect to DynamoDB
        dynamodb = boto3.resource(
            "dynamodb",
            region_name=context.aws_region,
            aws_access_key_id=context.aws_access_key_id,
            aws_secret_access_key=context.aws_secret_access_key,
            aws_session_token=context.aws_session_token
        )
        table = dynamodb.Table(context.dynamodb_table_name)
        
        # Check if table exists and is accessible
        _ = table.table_status
        
        # Get data files
        data_dir = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/out/dynamoDB")))
        if not data_dir.exists() or not data_dir.is_dir():
            logger.error("Data directory not found: %s", data_dir)
            return False
        
        json_files = list(data_dir.glob("*.json"))
        if not json_files:
            logger.error("No JSON files found in the directory: %s", data_dir)
            return False
        
        logger.info("Found %d JSON files to insert into DynamoDB", len(json_files))
        
        # Upload data
        for file_path in json_files:
            try:
                with file_path.open() as f:
                    items = json.load(f)
            except (OSError, json.JSONDecodeError):
                logger.exception("Failed to load file: %s", file_path)
                continue
            
            logger.info("Inserting %d items from %s...", len(items), file_path.name)
            
            for item in items:
                try:
                    table.put_item(Item=item)
                    context.inserted_items.append(item)
                except (boto3.exceptions.Boto3Error, BotoCoreError):
                    logger.exception("Failed to insert item %s", item.get("PK", "<unknown>"))
        
        logger.info("Inserted %d items from %d files", len(context.inserted_items), len(json_files))
        return len(context.inserted_items) > 0
    
    except (boto3.exceptions.Boto3Error, BotoCoreError) as e:
        logger.error("DynamoDB operation failed: %s", e)
        return False
    except Exception as e:
        logger.error("An unexpected error occurred: %s", e)
        return False