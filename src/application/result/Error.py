from application.math_objects.Scalar import Scalar
from application.result.Result import Result
from application.math_objects.Vector import Vector


class ScalarError:
    """
    A class containing measurement errors for given scalars.
    Attributes
    ----------
    abs: Scalar
        Absolute error.
    rel: Scalar
        Relative error (NaN if measured value is 0).
    """

    def __init__(self, x: Scalar, x0: Scalar):
        """
        Class constructor.
        Parameters
        ----------
        x: Scalar
            Measured value.
        x0: Scalar
            Model value.
        """
        self.abs = abs(x - x0)
        self.rel = self.abs / x if x != 0 else Scalar.nan()

    def __str__(self):
        return f"SError(abs={self.abs}, rel={self.rel})"


class VectorError:
    """
    A class containing measurement errors for given vectors.
    Attributes
    ----------
    x: ScalarError
        X cord error.
    y: ScalarError
        Y cord error.
    value: ScalarError
        Value error.
    """

    def __init__(self, vec: Vector, vec0: Vector):
        """
        Class constructor.
        Parameters
        ----------
        vec: Vector
            Measured Vector.
        vec0: Vector
            Model Vector.
        """
        self.x = ScalarError(vec.x, vec0.x)
        self.y = ScalarError(vec.y, vec0.y)
        self.value = ScalarError(vec.value, vec0.value)

    def __str__(self):
        return f"VError(x={self.x}, y={self.y}, value={self.value})"


class Error:
    """
    A class containing measurement errors for one cycle.
    Attributes
    ----------
    duration: ScalarError
        Full duration error.
    duration1: ScalarError
        1st to 2nd cycle point duration error.
    duration2: ScalarError
        2nd to 3rd cycle point duration error.
    start_velocity: VectorError
        Start velocity error.
    end_velocity: VectorError
        End velocity error.
    reach: VectorError
        Reach error.
    """

    def __init__(self, measure: Result, model: Result):
        """
        Class constructor.
        Parameters
        ----------
        measure: Result
            Measured Result.
        model: Result
            Model Result.
        """
        self.duration = ScalarError(measure.duration, model.duration)
        self.duration1 = ScalarError(measure.duration1, model.duration1)
        self.duration2 = ScalarError(measure.duration2, model.duration2)
        self.start_velocity = VectorError(measure.start_velocity, model.start_velocity)
        self.end_velocity = VectorError(measure.end_velocity, model.end_velocity)
        self.reach = VectorError(measure.reach, model.reach)

    def __str__(self):
        """
        Converts to string.
        """
        return (f"Error(duration={self.duration}, "
                f"duration1={self.duration1}, "
                f"duration2={self.duration2}, "
                f"start_velocity={self.start_velocity}, "
                f"end_velocity={self.end_velocity},"
                f"reach={self.reach})")
