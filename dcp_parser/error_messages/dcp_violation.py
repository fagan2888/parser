import abc
from dcp_parser.expression.curvature import Curvature
from dcp_parser.expression.sign import Sign
from dcp_parser.atomic.monotonicity import Monotonicity
import settings

class DCPViolation(object):
    """ Abstract base class for DCP Violations. """
    __metaclass__ = abc.ABCMeta

    # Maps curvature, monotonicity, and sign to the error message name.
    TYPE_TO_NAME = {
                str(Curvature.CONSTANT): 'constant',
                str(Curvature.AFFINE): 'affine',
                str(Curvature.CONVEX): 'convex',
                str(Curvature.CONCAVE): 'concave',
                str(Curvature.NONCONVEX): 'non-convex',
                str(Monotonicity.INCREASING): 'non-decreasing',
                str(Monotonicity.DECREASING): 'non-increasing',
                str(Monotonicity.NONMONOTONIC): 'non-monotonic',
                str(Sign.POSITIVE): 'positive',
                str(Sign.NEGATIVE): 'negative',
                str(Sign.ZERO): 'zero',
                str(Sign.UNKNOWN): 'unknown sign',
                }

    # Maps curvature and monotonicity to the error message name.
    @staticmethod
    def type_to_name(type):
        return DCPViolation.TYPE_TO_NAME[str(type)]

    # Returns whether the error is indexed as an argument in a function.
    # Distinguishes OperationErrors from CompositionErrors and ConstraintErrors
    def is_indexed(self):
        return hasattr(self, 'index')

    # Core error message
    @abc.abstractmethod
    def error_message(self):
        return NotImplemented

    # Error message with preamble
    def __str__(self):
        return settings.DCP_ERROR_MSG + self.error_message()
