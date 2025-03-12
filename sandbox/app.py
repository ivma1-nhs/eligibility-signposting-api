"""
proxy server for Stoplight Prism with response example selection logic

adapted from https://stackoverflow.com/a/36601467
"""

import logging
import os
import sys

import requests  # pyright: ignore [reportMissingModuleSource]
from flask import Flask, Request, Response, request  # pyright: ignore [reportMissingImports]

# Configure logging to output to stdout
logging.basicConfig(stream=sys.stdout, level=logging.INFO)


##---------------------------------------------------------------------
## Modify this function select an example based on the request.
##---------------------------------------------------------------------
def example_name(request: Request) -> str | None:
    """
    Given the whole request, return the `Prefer:` header value if a specific
    example is desired.  Otherwise, return `None`.
    """

    ## This can be as complex as you want.  You could load the OpenAPI
    ## document and invent your own DSL within it.  There are several
    ## ideas in https://github.com/stoplightio/prism/issues/1838.
    if "patient=0000000001" in request.full_path:
        return "example1"
    if "patient=0000000002" in request.full_path:
        return "example2"
    if "patient=0000000003" in request.full_path:
        return "code404"
    return None


##---------------------------------------------------------------------
## HTTP proxy to Prism
##---------------------------------------------------------------------
UPSTREAM_HOST = os.environ.get("UPSTREAM_HOST")
if not UPSTREAM_HOST:
    UPSTREAM_HOST_ERROR = "UPSTREAM_HOST environment variable not set"
    raise ValueError(UPSTREAM_HOST_ERROR)
app = Flask(__name__)
app.logger.setLevel("INFO")
session = requests.Session()


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def proxy_to_upstream(path: str) -> Response:  # noqa: ARG001
    headers_to_upstream = {k: v for k, v in request.headers if k.lower() != "host"}

    prefer_header_value = example_name(request)
    if prefer_header_value.startswith("example"):  # pyright: ignore [reportOptionalMemberAccess]
        prefer_header_value = f"example={prefer_header_value}"
        headers_to_upstream["prefer"] = prefer_header_value
    elif prefer_header_value.startswith("code"):  # pyright: ignore [reportOptionalMemberAccess]
        prefer_header_value = f"code={prefer_header_value[4:]}"  # pyright: ignore [reportOptionalSubscript]
        headers_to_upstream["prefer"] = prefer_header_value

    request_to_upstream = requests.Request(
        method=request.method,
        url=request.url.replace(request.host_url, UPSTREAM_HOST + "/"),  # pyright: ignore [reportOptionalOperand]
        headers=headers_to_upstream,
        data=request.get_data(),
        cookies=request.cookies,
    ).prepare()
    response_from_upstream = session.send(request_to_upstream)

    return Response(
        response_from_upstream.content,
        response_from_upstream.status_code,
        exclude_hop_by_hop(response_from_upstream.raw.headers),
    )


HOP_BY_HOP_HEADERS = [
    "connection",
    "content-encoding",
    "content-length",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "transfer-encoding",
    "transfer-encoding",
    "upgrade",
]

"""
Exclude hop-by-hop headers, which are meaningful only for a single
transport-level connection, and are not stored by caches or forwarded by
proxies. See https://www.rfc-editor.org/rfc/rfc2616#section-13.5.1.
"""


def exclude_hop_by_hop(headers: dict) -> list[tuple[str, str]]:
    return [(k, v) for k, v in headers.items() if k.lower() not in HOP_BY_HOP_HEADERS]
