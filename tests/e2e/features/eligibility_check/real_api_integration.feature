Feature: Full mTLS integration with real Eligibility API

  Background:
    Given AWS credentials are loaded from the environment
    And mTLS certificates are downloaded and available in the out/ directory

  Scenario Outline: Eligibility check returns 200 OK for valid NHS number
    Given I have the NHS number "<nhs_number>"
    When I query the eligibility API with mTLS
    Then the response status code should be 200
    And the response should be valid JSON

    Examples:
      | nhs_number    |
      | 50000000001   |
      | 50000000004   |