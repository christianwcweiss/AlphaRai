

class EpicNotFoundError(Exception):
    def __init__(self, epic):
        self.message = f"Epic {epic} not found"
        super().__init__(self.message)