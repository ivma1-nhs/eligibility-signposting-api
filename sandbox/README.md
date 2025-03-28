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

This will start the sandbox environment on localhost port 9000.

```bash
make down
```

This will stop the sandbox environment.

### Example curl calls

There are a number of examples of responses which can be returned by passing specific NHS Numbers in the patient query parameter:

```bash
 curl -X GET "http://0.0.0.0:9000/eligibility-check?patient=<patient NHS Number>" -H "Authorization: Bearer sdvsd"
```

#### Example scenarios

| Patient ID   | Response                                         |
|--------------|--------------------------------------------------|
| 50000000001  | RSV - Actionable CP Booking                      |
| 50000000002  | RSV - Actionable Non-CP Booking                  |
| 50000000003  | RSV - Eligible, not Actionable                   |
| 50000000004  | RSV - Not Eligible due to vaccination            |
| 50000000005  | RSV - Not Eligible due to not being in a cohort  |
| 50000000006  | RSV - No rules                                   |
| 90000000400  | Invalid input data                               |
| 90000000404  | Person not found                                 |
| 90000000422  | Unrecognised input data. (Unprocessable Content) |
| 90000000500  | Internal server error                            |

See [app.py](app.py) for current examples.
