# Sandbox environment

The sandbox environment uses:

* [OpenAPI Generator CLI](https://github.com/OpenAPITools/openapi-generator-cli) to validate the specification and convert it from .yaml to .json for use in the sandbox.
* [Prism](https://stoplight.io/open-source/prism) as a mock server.
* A flask proxy to allow us to inject specific examples based on request attributes.

## Developer instructions

Run the following command to start the sandbox environment:

```bash
make spec
make up
```

This will start the sandbox environment on localhost port 5000.

```bash
make down
```

This will stop the sandbox environment.

### Example curl calls

patient 0000000001 is a patient eligible and bookable for a Flu vaccination.

```bash
 curl -X GET "http://0.0.0.0:5000/eligibility?patient=0000000001" -H "Accept: application/json" -H "Authorization: Bearer sdvsd"
```

See [app.py](app.py) for more examples.
