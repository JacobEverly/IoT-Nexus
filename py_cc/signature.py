
class Signature:
    def __init__(self, r, s, recovery_id=None):
        self.r = r
        self.s = s
        self.recovery_id = recovery_id

    def toString(self):
        return f"r:{self.r},s:{self.s}"

    def __str__(self):
        return f"r: {self.r}, s: {self.s}"
    
    def __repr__(self):
        return f"Signature({self.r}, {self.s}, {self.recovery_id})"