from math import cos, sin, pi

from application.math_objects.Scalar import Scalar
from application.math_objects.Vector import Vector
from infrastructure.constants import SIM_SCALE, UNIT_VELOCITY, UNIT_MASS, UNIT_TILT
from application.exceptions import InputParsingError

MSG_OUT_OF_BOUNDS = "Input value out of bounds. Name={} Bounds={} Given={}"


def convert_to_scalar(string: str, unit: str | None) -> Scalar:
    str_list = list(string)
    pi_n = 0
    for i in range(0, len(str_list)):
        if str_list[i] == ",":
            str_list[i] = "."
        if str_list[i] == "p" or str_list[i] == "P":
            str_list[i] = ""
            pi_n += 1
    string = "".join(str_list)
    return Scalar(float(string) if pi_n == 0 else float(string) * pi_n * pi, unit)


def is_in_bounds(scalar: Scalar, floor_bound: float | None, ceil_bound: float | None):
    if floor_bound is not None:
        if scalar <= floor_bound:
            return False
    if ceil_bound is not None:
        if scalar >= ceil_bound:
            return False
    return True


class Input:
    """
    A class storing user-provided properties of simulation.
    Attributes
    ----------
    tilt : float
        Tilt of the plane (radians).
    mass : float
        Mass of the block.
    velocity : Vector
        Starting velocity of the block.
    friction : float
        Coulomb friction coefficient between the block and the plane.
    """

    @staticmethod
    def parse_tilt(tilt: str) -> Scalar:
        """
        Parses tilt from user input.
        Parameters
        ----------
        tilt: str
            User's tilt input.

        Returns
        -------
        tilt: Scalar
            Parsed Scalar tilt.
        """
        tilt_floor = 0
        tilt_ceil = 0.5 * pi

        scalar = convert_to_scalar(tilt, UNIT_TILT)
        if not is_in_bounds(scalar, 0, 0.5 * pi):
            raise InputParsingError(MSG_OUT_OF_BOUNDS.format("tilt", f"(0, 0.5pi)", scalar.value))
        return scalar

    @staticmethod
    def parse_mass(mass: str) -> Scalar:
        """
        Parses mass from user input.
        Parameters
        ----------
        mass: str
            User's input.

        Returns
        -------
        mass: Scalar
            Parsed Scalar mass.
        """
        scalar = convert_to_scalar(mass, UNIT_MASS)
        if not is_in_bounds(scalar, 0, None):
            raise InputParsingError(MSG_OUT_OF_BOUNDS.format("mass", f"(0, inf)", scalar.value))
        return scalar


    @staticmethod
    def parse_velocity(velocity: str, tilt: Scalar) -> Vector:
        """
        Parses velocity from user input.
        Parameters
        ----------
        velocity: str
            User's input (velocity parallel to plane).
        tilt: Scalar
            Tilt of plane (radians).

        Returns
        -------
        velocity: Vector
            Parsed Vector velocity.
        """
        scalar = convert_to_scalar(velocity, UNIT_VELOCITY)
        if not is_in_bounds(scalar, 0, None):
            raise InputParsingError(MSG_OUT_OF_BOUNDS.format("velocity", f"(0, inf)", scalar.value))
        return Vector(scalar * cos(tilt.value), scalar * sin(tilt.value))

    @staticmethod
    def parse_friction(friction: str) -> Scalar:
        """
        Parses friction from user input.
        Parameters
        ----------
        friction: str
            User's input.

        Returns
        -------
        friction: Scalar
            Parsed Scalar friction.
        """
        scalar = convert_to_scalar(friction, None)
        if not is_in_bounds(scalar, 0, None):
            raise InputParsingError(MSG_OUT_OF_BOUNDS.format("friction", f"(0, inf)", scalar.value))
        return scalar

    def __init__(self, _tilt: Scalar, _mass: Scalar, _velocity: Vector, _friction: Scalar):
        """
        Class constructor.
        Parameters
        ----------
        _tilt: Scalar
            Tilt of the plane (radians).
        _mass: Scalar
            Mass of the block (kilograms).
        _velocity: Vector
            Starting velocity of the block (m/s).
        _friction: Scalar
            Coulomb friction coefficient between the block and the plane.
        """
        self.tilt = _tilt
        self.mass = _mass
        self.velocity = _velocity
        self.friction = _friction

    @classmethod
    def user(cls, _tilt: str, _mass: str, _velocity: str, _friction: str):
        """
        Creates Input instance from user input.
        Parameters
        ----------
        _tilt: str
            Tilt from user's input.
        _mass: str
            Mass from user's input.
        _velocity: str
            Velocity from user's input.
        _friction: str
            Friction from user's input.

        Returns
        -------
        input: Input
            Input instance.
        """
        tilt = cls.parse_tilt(_tilt)
        return cls(tilt, cls.parse_mass(_mass), cls.parse_velocity(_velocity, tilt),
                   cls.parse_friction(_friction))

    @classmethod
    def simulation(cls, _user_input):
        """
        Converts Input object so it is ready for simulation.
        :param _user_input: User's Input.
        :returns: Input instance.
        """
        return cls(
            _user_input.tilt,
            _user_input.mass * SIM_SCALE,
            _user_input.velocity * SIM_SCALE,
            _user_input.friction
        )

    def __str__(self):
        """
        Converts to string.
        """
        return (f"Input(tilt={self.tilt}, "
                f"mass={self.mass}, "
                f"velocity={self.velocity}, "
                f"friction={self.friction})")
