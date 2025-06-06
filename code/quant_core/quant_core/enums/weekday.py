from enum import Enum


class Weekday(Enum):
    """Enumeration for days of the week."""

    MONDAY = "Monday"
    TUESDAY = "Tuesday"
    WEDNESDAY = "Wednesday"
    THURSDAY = "Thursday"
    FRIDAY = "Friday"
    SATURDAY = "Saturday"
    SUNDAY = "Sunday"

    def __str__(self) -> str:
        return self.value

    def to_number(self) -> int:
        """Convert the weekday to a number (0=Monday, 6=Sunday)."""
        return list(Weekday).index(self)

    @staticmethod
    def from_number(number: int) -> "Weekday":
        """Convert a number to a Weekday enum."""
        if number < 0 or number > 6:
            raise ValueError("Number must be between 0 and 6.")
        return list(Weekday)[number]
