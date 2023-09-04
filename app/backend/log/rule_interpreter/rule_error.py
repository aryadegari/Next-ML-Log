# Can add more functionality if needed
class RuleError(Exception):
    def __init__(self, error: str):
        self.error: str = error

    def __str__(self) -> str:
        return self.error
