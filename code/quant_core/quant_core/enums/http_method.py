from enum import Enum


class HTTPMethod(Enum):
    """HTTP methods for API requests."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
