from gromet import *


# -----------------------------------------------------------------------------
# Experiment Spec
# -----------------------------------------------------------------------------

@dataclass
class Measure(GrometElm):
    """
    Defines a Measure.
    'source' references the UidPort or UidJunction whose value will be measured.
    'interval':
    'type':
    """
    measure_id: UidMeasure
    source: Union[UidPort, UidJunction]
    interval: None  # TODO: Tuple or Array
    type: UidType  # Enum("M:instance", "M:interval", "M:steady_state")


@dataclass
class ParameterAssignment(Valued):
    """
    Specifies the value for a parameter in the model.
    The 'source' identifies the Port or Junction that will be set.
    This class extends Valued, so it has a value and value_type.
    If 'value' is None:
        use value already present in source as the parameter value.
    If 'value' is not None:
        use this value as the parameter value.

    """
    source: Union[UidPort, UidJunction]


@dataclass
class Fold(GrometElm):
    """
    A Fold applies an expression across one or more Measure or the
    result of another Fold.
    Including Fold(s) in the args list permits building more complex
    Folds that build on the results of other Folds.
    A Fold could be specified that itself takes no arguments and has
    an Expression just "generates" a sequence of numbers (a predefined
    sequence).
    Expression type is required for the expression because we need to
    define the Ports that may be accessed in the Expr tree, but have
    the order of those Ports correspond to the order of the Fold args
    list.
    """
    args: List[Union[UidMeasure, 'Fold']]
    expression: Expression
    # TODO
    #  Need easy way to just specify an array of raw values
    #  Could enable Expr to just "return" a vector of raw values,
    #      then in Expression
    #  But I don't like that. Prefer extending Literal to LiteralRaw
    #      that can take a JSON list of raw values...?


@dataclass
class ExperimentSpec(GrometElm, ABC):
    measures: List[Measure]
    folds: List[Fold]
    parameters: List[ParameterAssignment]  # initial conditions


@dataclass
class FrontendExperimentSpec(ExperimentSpec):
    """
    Message sent by HMI to Proxy
    """
    model_id: UidGromet


@dataclass
class BackendExperimentSpec(ExperimentSpec):
    """
    Message sent from Proxy to Backend
    """
    model: Gromet


@dataclass
class ExperimentSpecSet(GrometElm):
    experiments: List[ExperimentSpec]


@dataclass
class ExperimentResults(GrometElm):
    measurements: List[Tuple[UidMeasure, List[Any]]]
