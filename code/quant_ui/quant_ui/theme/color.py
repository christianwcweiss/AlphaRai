class Color:
    def __init__(self, hex_code: str) -> None:
        self._hex_code = hex_code

    @property
    def hex_code(self) -> str:
        return self._hex_code

    def __str__(self):
        return self._hex_code

    def __repr__(self):
        return self._hex_code

    def __eq__(self, other: "Color"):
        return self.hex_code == other.hex_code
