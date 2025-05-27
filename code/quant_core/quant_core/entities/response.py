import json
from http import HTTPStatus
from typing import Dict, Any


class Response:
    """
    Represents an HTTP response with a status code and a message.
    """

    def __init__(self, http_status: HTTPStatus, message: str) -> None:
        """
        Initializes a Response instance.
        """
        self._http_status = http_status
        self._message = message

    @property
    def http_status(self) -> HTTPStatus:
        """Gets the HTTP status code of the response."""
        return self._http_status

    @property
    def message(self) -> str:
        """Gets the message body of the response."""
        return self._message

    def to_response(self) -> Dict[str, Any]:
        """
        Converts the Response object to a dictionary suitable for HTTP responses.
        """
        return {"statusCode": self._http_status.value, "body": json.dumps({"message": self._message})}
