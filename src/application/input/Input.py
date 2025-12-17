"""
Copyright 2025 Jan Oleński

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied. See the License for the specific language governing
permissions and limitations under the License.
"""
import logging
from math import cos, sin

from application.exceptions import InputParsingError, InputField
from application.math_objects.Scalar import Scalar
from application.math_objects.Vector import Vector
from infrastructure.Config import *

MSG_TOO_BIG = "Input value too big. Max={} Given={}"
MSG_TOO_SMALL = "Input value too small. Min={} Given={}"
MSG_CONVERT = "Input value can not be converted to Scalar. Value={} Unit={}"


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
        try:
            tilt = parse_scalar(_tilt, UNIT_TILT, TILT_MIN, TILT_MAX)
        except InputParsingError as e:
            logging.error(f"Error while parsing user's input: e={e} tilt={_tilt}")
            raise InputParsingError(e.desc, InputField.TILT)

        try:
            mass = parse_scalar(_mass, UNIT_MASS, MASS_MIN, MASS_MAX)
        except InputParsingError as e:
            logging.error(f"Error while parsing user's input: mass={_mass}")
            raise InputParsingError(e.desc, InputField.MASS)

        try:
            velocity = parse_velocity(_velocity, tilt)
        except InputParsingError as e:
            logging.error(f"Error while parsing user's input: e={e} velocity={_velocity}")
            raise InputParsingError(e.desc, InputField.VELOCITY)

        try:
            friction = parse_scalar(_friction, None, FRICTION_MIN, FRICTION_MAX)
        except InputParsingError as e:
            logging.error(f"Error while parsing user's input: e={e} friction={_friction}")
            raise InputParsingError(e.desc, InputField.FRICTION)
        return cls(tilt, mass, velocity, friction)

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


def convert_to_scalar(string: str, unit: str | None) -> Scalar:
    str_list = list(string)
    pi_n = 0
    for i in range(0, len(str_list)):
        if str_list[i] == ",":
            str_list[i] = "."
        if str_list[i] == "p" or str_list[i] == "P":
            str_list[i] = ""
            pi_n += 1
    new_string = "".join(str_list)
    try:
        return Scalar(float(new_string) if pi_n == 0 else float(new_string) * pi_n * pi, unit)
    except ValueError as e:
        logging.error(f"ValueError: {e}")
        logging.error(f"Input value can not be converted to Scalar: string={string} unit={unit}")
        raise InputParsingError.no_field(MSG_CONVERT.format(string, unit))


def check_bounds(scalar: Scalar, floor_bound: float | None, ceil_bound: float | None) -> None:
    if floor_bound is not None:
        if scalar <= floor_bound:
            logging.error(f"Input value too small: min={floor_bound} given={scalar}")
            raise InputParsingError.no_field(MSG_TOO_SMALL.format(floor_bound, scalar.value))
    if ceil_bound is not None:
        if scalar >= ceil_bound:
            logging.error(f"Input value too big: max={ceil_bound} given={scalar}")
            raise InputParsingError.no_field(MSG_TOO_BIG.format(ceil_bound, scalar.value))


def parse_scalar(value: str, unit: str | None, min_value: float | None, max_value: float | None) -> Scalar:
    """
    Parses scalar value from user input.
    Parameters
    ----------
    value: str
        User's input value.
    unit: str | None
        Expected unit of value.
    min_value: float | None,
        Minimum value.
    max_value: float | None
        Maximum value.

    Returns
    -------
    value: Scalar
        Parsed value.
    """
    scalar = convert_to_scalar(value, unit)
    check_bounds(scalar, min_value, max_value)
    return scalar


def parse_velocity(velocity: str, tilt: Scalar) -> Vector:
    """
    Parses velocity from user input.
    Parameters
    ----------
    velocity: str
        User's velocity input.
    tilt: Scalar
        Tilt of plane.

    Returns
    -------
    velocity: Vector
        Parsed user's velocity.
    """
    scalar = convert_to_scalar(velocity, UNIT_VELOCITY)
    check_bounds(scalar, VELOCITY_MIN, VELOCITY_MAX)
    return Vector(scalar * cos(tilt.value), scalar * sin(tilt.value))
