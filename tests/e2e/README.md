# Eligibility Signposting API Test Automation Framework

This repository contains a Python-based test automation framework for the Eligibility Signposting API. The framework uses Behave for BDD-style tests and requests library to implement API tests with mTLS authentication.

## Framework Structure

```bash
tests/e2e/
├── data/
│   ├── out/                               # Generated test data and certificates
│   │   ├── dynamoDB/                      # Generated DynamoDB data
│   │   └── *.pem                          # mTLS certificates
│   └── *.json                             # Test data templates
├── features/
│   ├── eligibility_check/
│   │   ├── eligibility_check.feature      # Basic Behave feature file
│   │   └── real_api_integration.feature   # mTLS integration feature file
│   ├── steps/
│   │   ├── eligibility_check_steps.py     # Basic step definitions
│   │   └── mtls_steps.py                  # mTLS integration step definitions
│   └── environment.py                     # Behave environment hooks
├── utils/
│   ├── api_client.py                      # Reusable HTTP client
│   ├── config.py                          # Environment config and schemas
│   ├── data_loader.py                     # Test data generation and loading
│   └── mtls.py                            # mTLS certificate management
└── .env                                   # Environment variables (not in version control)
```

## Setup and Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/ivma1-nhs/qa-automation.git
   cd qa-automation
   ```

2. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install Poetry (if not already installed):

   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   # Or see https://python-poetry.org/docs/#installation for details
   ```

4. Install dependencies:

   ```bash
   poetry install
   ```

5. Configure environment variables:
   - Copy the `.env.example` file to `.env` (if not already present)
   - Update the values in `.env` with your sandbox credentials

## Running Tests

### Running BDD tests with Behave

Run all Behave feature tests:

```bash
cd tests/e2e
behave
```

Run a specific feature file:

```bash
cd tests/e2e
behave --format pretty features/eligibility_check/eligibility_check.feature
```

Run the mTLS integration tests:

```bash
cd tests/e2e
behave --format pretty features/eligibility_check/real_api_integration.feature
```

This will discover and run all feature files in the `features/` directory using Behave.

### Environment Variables

The following environment variables are required for the mTLS integration tests:

```
# AWS Credentials
AWS_REGION=eu-west-2
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_SESSION_TOKEN=your-session-token  # Optional

# API Configuration
API_GATEWAY_URL=https://test.eligibility-signposting-api.nhs.uk

# DynamoDB Configuration
DYNAMODB_TABLE_NAME=eligibilty_data_store
```

These can be set in the `.env` file in the `tests/e2e` directory.

## Extending the Framework

### Adding New BDD Tests (Behave)

1. Create a new feature file:

   ```gherkin
   # features/new_feature/new_feature.feature
   Feature: New Feature
     As a user of the Eligibility Signposting API
     I want to use the new feature
     So that I can achieve my goal

     Scenario: Successful use of new feature
       Given the API is available
       When I make a request to the new feature endpoint
       Then the response should be successful
   ```

2. Create step definitions:

   ```python
   # features/steps/new_feature_steps.py
   from behave import given, when, then

   @when('I make a request to the new feature endpoint')
   def step_impl_make_request(context):
       # Implementation
       pass

   @then('the response should be successful')
   def step_impl_check_success(context):
       # Implementation
       pass
   ```

3. Run the BDD tests with:

   ```bash
   cd tests/e2e
   behave
   ```

### Adding New API Endpoints

1. Update the config.py file with the new endpoint:

   ```python
   # utils/config.py
   NEW_ENDPOINT = '/new-endpoint'
   ```

2. Add a new method to the ApiClient class:

   ```python
   # utils/api_client.py
   def get_new_endpoint(self, param1, param2):
       url = f"{self.base_url}/new-endpoint"
       params = {"param1": param1, "param2": param2}
       response = requests.get(url, headers=self.headers, params=params)
       return response
   ```

### Adding New Response Schemas

1. Add the new schema to config.py:

   ```python
   # utils/config.py
   NEW_ENDPOINT_SCHEMA = {
       "type": "object",
       "properties": {
           # Schema definition
       }
   }
   ```

2. Use the schema in your tests:

   ```python
   from utils.config import NEW_ENDPOINT_SCHEMA
   import jsonschema

   @then('the response should match the new endpoint schema')
   def step_impl_check_schema(context):
       response_json = context.response.json()
       jsonschema.validate(instance=response_json, schema=NEW_ENDPOINT_SCHEMA)
   ```

### Adding DynamoDB Integration

When the DynamoDB-backed API is ready, you can extend the framework by:

1. Adding DynamoDB client configuration:

   ```python
   # utils/dynamo_client.py
   import boto3
   from utils.config import AWS_REGION, AWS_ACCESS_KEY, AWS_SECRET_KEY

   class DynamoClient:
       def __init__(self):
           self.client = boto3.client(
               'dynamodb',
               region_name=AWS_REGION,
               aws_access_key_id=AWS_ACCESS_KEY,
               aws_secret_access_key=AWS_SECRET_KEY
           )

       def get_item(self, table_name, key):
           response = self.client.get_item(
               TableName=table_name,
               Key=key
           )
           return response
   ```

2. Using the DynamoDB client in step definitions:

   ```python
   # features/steps/dynamo_steps.py
   from behave import given, when, then
   from utils.dynamo_client import DynamoClient

   @given('I have a DynamoDB client')
   def step_impl_dynamo_client(context):
       context.dynamo_client = DynamoClient()

   @when('I query DynamoDB for item with key "{key}"')
   def step_impl_query_dynamo(context, key):
       context.dynamo_response = context.dynamo_client.get_item(
           "my_table", {"id": {"S": key}}
       )
   ```

## Best Practices

1. **Test Independence**: Each test should be independent and not rely on the state from other tests.
2. **Reusable Steps**: Create reusable step definitions that can be used across multiple feature files.
3. **Multiple Test Cases**: Use Scenario Outlines for testing multiple scenarios with different data.
4. **Assertions**: Use descriptive assertions to make test failures clear.
5. **Documentation**: Document your tests with clear feature descriptions and step definitions.
6. **Environment Variables**: Use environment variables for sensitive information and configuration.

## Continuous Integration

This framework can be integrated with CI/CD pipelines:

1. Add a GitHub Actions workflow:

   ```yaml
   # .github/workflows/test.yml
   name: API Tests

   on:
     push:
       branches: [ main ]
     pull_request:
       branches: [ main ]

   jobs:
     test:
       runs-on: ubuntu-latest
       steps:
       - uses: actions/checkout@v2
       - name: Set up Python
         uses: actions/setup-python@v2
         with:
           python-version: '3.9'
       - name: Install dependencies
         run: |
           poetry install
       - name: Run tests
         run: |
           cd tests/e2e
           behave --format pretty --outfile behave-report.txt
         env:
           BASE_URL: ${{ secrets.BASE_URL }}
           API_KEY: ${{ secrets.API_KEY }}
       - name: Upload test report
         uses: actions/upload-artifact@v2
         with:
           name: test-report
           path: tests/e2e/behave-report.txt
   ```