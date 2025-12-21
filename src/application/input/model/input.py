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
from math import cos, sin, pi

from application.input.exceptions import InputParsingError
from application.input.model.input_field import InputField
from application.math.scalar import Scalar
from application.math.vector import Vector
from infrastructure.config.config import CONFIG

MSG_TOO_BIG = "Input value too big. Max={} Given={}"
MSG_TOO_SMALL = "Input value too small. Min={} Given={}"
MSG_CONVERT = "Input value can not be converted to Scalar. Value={} Unit={}"


class Input:
    """A class storing constants of simulation.

    Attributes:
        tilt: Scalar: A tilt angle of the plane.
        mass: Scalar: A mass of the point.
        velocity: Vector: A start velocity of the point.
        friction: Scalar: A friction coefficient between the plane and the point.

    """

    def __init__(self, tilt: Scalar, mass: Scalar, velocity: Vector, friction: Scalar):
        """Class constructor.

        :param tilt: Scalar
        :param mass: Scalar
        :param velocity: Vector
        :param friction: Scalar

        """
        self.tilt: Scalar = tilt
        self.mass: Scalar = mass
        self.velocity: Vector = velocity
        self.friction: Scalar = friction

    @classmethod
    def user(cls, tilt: str, mass: str, velocity: str, friction: str):
        """Creates Input instance from unparsed input.

        :param tilt: str: Unparsed tilt.
        :param mass: str: Unparsed mass.
        :param velocity: str: Unparsed velocity.
        :param friction: str: Unparsed friction.
        
        """
        try:
            s_tilt = parse_scalar(tilt, CONFIG.unit.tilt, CONFIG.input.min_tilt, CONFIG.input.max_tilt)
        except InputParsingError as e:
            logging.error(f"Error while parsing user's input: e={e} tilt={tilt}")
            raise InputParsingError(e.desc, InputField.TILT)

        try:
            s_mass = parse_scalar(mass, CONFIG.unit.mass, CONFIG.input.min_mass, CONFIG.input.max_mass)
        except InputParsingError as e:
            logging.error(f"Error while parsing user's input: mass={mass}")
            raise InputParsingError(e.desc, InputField.MASS)

        try:
            s_vel = parse_velocity(velocity, s_tilt)
        except InputParsingError as e:
            logging.error(f"Error while parsing user's input: e={e} velocity={velocity}")
            raise InputParsingError(e.desc, InputField.VELOCITY)

        try:
            s_friction = parse_scalar(friction, None, CONFIG.input.min_friction, CONFIG.input.max_friction)
        except InputParsingError as e:
            logging.error(f"Error while parsing user's input: e={e} friction={friction}")
            raise InputParsingError(e.desc, InputField.FRICTION)
        return cls(s_tilt, s_mass, s_vel, s_friction)

    @classmethod
    def simulation(cls, user_input):
        """Converts parsed Input object for the simulation.

        :param user_input: Input: The user's input.

        """
        return cls(
            user_input.tilt,
            user_input.mass * CONFIG.scale,
            user_input.velocity * CONFIG.scale,
            user_input.friction
        )

    def __str__(self):
        return (f"Input(tilt={self.tilt} "
                f"mass={self.mass} "
                f"velocity={self.velocity} "
                f"friction={self.friction})")


def convert_to_scalar(string: str, unit: str | None) -> Scalar:
    """Converts unparsed scalar value to Scalar.

    :param string: str: Unparsed value.
    :param unit: (str | None): Unit.
    :returns: Scalar
    """
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
    """Checks if Scalar is within given bounds.

    :param scalar: Scalar: Checked value.
    :param floor_bound: (float | None): < scalar
    :param ceil_bound: (float | None): > scalar

    """
    if floor_bound is not None:
        if scalar <= floor_bound:
            logging.error(f"Input value too small: min={floor_bound} given={scalar}")
            raise InputParsingError.no_field(MSG_TOO_SMALL.format(floor_bound, scalar.value))
    if ceil_bound is not None:
        if scalar >= ceil_bound:
            logging.error(f"Input value too big: max={ceil_bound} given={scalar}")
            raise InputParsingError.no_field(MSG_TOO_BIG.format(ceil_bound, scalar.value))


def parse_scalar(value: str, unit: str | None, bigger_than: float | None, smaller_than: float | None) -> Scalar:
    """Parses scalar value.

    :param value: str: Unparsed value.
    :param unit: (str | None): Value's unit.
    :param bigger_than: (float | None): Must be bigger than value.
    :param smaller_than: (float | None): Must be smaller than value.

    """
    scalar = convert_to_scalar(value, unit)
    check_bounds(scalar, bigger_than, smaller_than)
    return scalar


def parse_velocity(velocity: str, tilt: Scalar) -> Vector:
    """Parses velocity.

    :param velocity: str: Unparsed velocity.
    :param tilt: Scalar: A tilt angle of the plane.
    """
    scalar = convert_to_scalar(velocity, CONFIG.unit.velocity)
    check_bounds(scalar, CONFIG.input.min_velocity, CONFIG.input.max_velocity)
    return Vector(scalar * cos(tilt.value), scalar * sin(tilt.value))
