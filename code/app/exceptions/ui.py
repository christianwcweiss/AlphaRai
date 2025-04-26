


class ComponentPropertyError(Exception):
    """Exception raised when a component property is invalid."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message