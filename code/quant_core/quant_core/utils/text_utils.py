import random
import re
import string


def camel_case_to_snake_case(name: str) -> str:
    """
    Convert camel case name to snake case name.
    """
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def generate_uid(prefix: str = "", length: int = 8) -> str:
    """Generate a random UID of the specified length."""
    return prefix + "".join(random.choices(string.ascii_uppercase + string.digits, k=length))
