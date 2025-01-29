import re


def camel_case_to_snake_case(name: str) -> str:
    """
    Convert camel case name to snake case name.
    """
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()
