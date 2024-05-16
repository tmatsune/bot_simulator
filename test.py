from settings import * 


class Test(Enum):
    ZERO = 0,
    ONE = 1,
    TWO = 2


@dataclass
class Struct:
    num: int
    val: str

struct = Struct(10, "struct")
print(struct)