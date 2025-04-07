# Vaccination Eligibility Data Product - Specification

## Overview

The `eligibility-signposting-api` is based on an OpenAPI specification maintained at `/specification/eligibility-signposting-api.yaml`. We use [Redocly CLI](https://redocly.com/docs/cli) to inject environment-specific elements into the base specification, allowing us to publish to different environments without manual editing or maintaining duplicate specifications.

## Directory Structure

### `components/security/`

Contains environment-specific security configurations for each endpoint.

### `x-nhsd-apim/`

Contains APIM extensions to the OpenAPI specification with deployment requirements:

- **access**: Environment-specific access patterns
- **ratelimit**: API rate limiting configurations
- **target**: API backend details for proxy configuration

## Generating Environment-Specific Specifications

To build a specification for a specific environment:

1. Set the target environment using the `APIM_ENV` parameter
2. Run `make construct-spec` from the repository root, which:
   - Updates templates with environment-specific values
   - Uses Redocly to compile the complete specification to `build/specification/`
   - For the `sandbox` environment, automatically runs `make publish` to convert the specification to JSON and save it to `sandbox/specification/` for immediate use
