import json
from dataclasses import dataclass, field, asdict
from dataclasses_json import dataclass_json


@dataclass
class A(object):
    gromet_elm: str = field(init=False)

    def __post_init__(self):
        self.gromet_elm = type(self).__name__


# @dataclass_json  # required in order to get .to_dict() interface
@dataclass
class B(A):
    name: str
    type: str


@dataclass
class C(B):
    val: int


@dataclass
class D(B):
    val: int

    # NOTE: json.dumps is not natively able to walk dataclass
    # member objects
    # If class B includes an initial decorator of @dataclass_json
    # (from the dataclasses_json package), then it will work,
    # *IF* you call .to_dict() on the object within the json_dumps call
    member: B


if __name__ == "__main__":
    b = B("myB", type="B")
    print(json.dumps(b.__dict__))
    c = C("myB", type="C", val=3)
    print(json.dumps(c.__dict__))

    z = D("myB", type="D", val=3, member=b)

    # If you
    #   (1) comment-out line 14 above, removing the
    #       @dataclass_json decorator on class B, AND
    #   (2) uncomment line 52 below...
    # you will get an error that:
    #     Object of type B is not JSON serializable.
    print(json.dumps(asdict(z)))

    # If you use the @dataclasses-json decorator (from the
    # dataclasses_json package) before the @dataclass
    # decorator on class B, then this will work:
    # (NOTE use of .to_dict() instead of .__dict__)
    # print(json.dumps(z.to_dict()))
