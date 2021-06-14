from gromet import *
from typing import Any


# -----------------------------------------------------------------------------
# Experiment Spec
# -----------------------------------------------------------------------------

@dataclass
class Measure(GrometElm):
    """
    Defines a Measure.
    'source' references the UidPort or UidJunction whose value will be measured.
    'interval': either a list of time points or a tuple (<start>, <end>)
    'type':
    """
    measure_id: UidMeasure
    source: Union[UidPort, UidJunction]
    interval: Union[List[float], Tuple[float, float]]
    type: UidType  # Enum("M:instance", "M:interval", "M:steady_state")


@dataclass
class ParameterAssignment(Valued):
    """
    Specifies the value for a parameter in the model.
    The 'source' identifies the Port or Junction that will be set.
    This class extends Valued, so it has a 'value' and 'value_type'.
    If 'value' is None:
        execution framework will use value already present in source
        as the (initial) parameter value.
    If 'value' is not None:
        execution framework will use the provided value Literal as
        the (initial) parameter value.

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
    an Expression that just "generates" a sequence of numbers (a
    predefined sequence).
    Expression type is required for the expression because we need to
    define the Ports that may be accessed in the Expr tree;
    the order of those Ports corresponds to the order of the Fold args
    list, for mapping "inputs" to the Expression.
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
    """
    Base Experiment Specification.
    """
    measures: List[Measure]
    folds: List[Fold]
    parameters: List[ParameterAssignment]  # initial conditions


@dataclass
class FrontendExperimentSpec(ExperimentSpec):
    """
    Message sent by HMI to Proxy.
    Only references model by it's GroMEt Uid.
    """
    model_id: UidGromet


@dataclass
class BackendExperimentSpec(ExperimentSpec):
    """
    Message sent from Proxy to Backend.
    Includes GroMEt payload (assumes proxy retrieves GroMEt from store).
    """
    model: Gromet


@dataclass
class ExperimentSpecSet(GrometElm):
    """
    A collection of experiment specifications.
    """
    experiments: List[ExperimentSpec]


@dataclass
class ExperimentResults(GrometElm):
    """
    Results of an experiment.
    'measurements' is a collection of tuples of:
        <Uid of Measure>, <sequence of values (anything)>
    In the case of indexed return values, the sequence of values
        will be tuples: (<index>, <value>)
    """
    measurements: List[Tuple[UidMeasure, List[Any]]]
