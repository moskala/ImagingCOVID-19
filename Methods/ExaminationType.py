from enum import Enum
class ExaminationType(Enum):
    CT = 0
    XRAY = 1

    def __str__(self):
        dictionary = {
            0: "Computer\ntomography",
            1: "X-Ray"
        }
        return dictionary[self.value]
