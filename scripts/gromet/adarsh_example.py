import json
from dataclasses import dataclass, field

@dataclass
class A(object):
    type: str = field(init=False)

    def __post_init__(self):
        self.gromet_class = type(self).__name__

@dataclass
class B(A):
    pass

if __name__ == "__main__":
    x = B()
    print(json.dumps(x.__dict__))
