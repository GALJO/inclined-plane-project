from math import sin, cos, pi

from _pytest.raises import raises

from src.Input import Input, MSG_OUT_OF_BOUNDS
from src.Scalar import Scalar
from src.Vector import Vector
from src.constants import UNIT_TILT, UNIT_MASS, UNIT_VELOCITY, MATH_PRECISION
from src.exceptions import InputParsingError


def test_parsing_tilt():
    # given
    model = Scalar(0.79, UNIT_TILT)
    model_pi = Scalar(0.25 * pi, UNIT_TILT)
    model_comma = Scalar(0.79, UNIT_TILT)

    # when
    tilt = Input.parse_tilt("0.79")
    tilt_pi = Input.parse_tilt("0.25p")
    tilt_comma = Input.parse_tilt("0,79")

    # then
    assert tilt == model
    assert tilt_pi == model_pi
    assert tilt_comma == model_comma


def test_parsing_tilt_out_of_bounds():
    # given
    tilts = [0.0, -5.0, 0.5 * pi, pow(0.1, MATH_PRECISION + 1), (0.5 * pi) - pow(0.1, MATH_PRECISION + 1)]

    for tilt in tilts:
        with raises(InputParsingError) as e:
            # when
            Input.parse_tilt(str(tilt))
            # then
            assert e.value.desc == MSG_OUT_OF_BOUNDS.format("tilt", f"(0, 0.5pi)", round(tilt, MATH_PRECISION))


def test_parsing_mass():
    # given
    model = Scalar(10, UNIT_MASS)
    model_comma = Scalar(20.5, UNIT_MASS)

    # when
    mass = Input.parse_mass("10")
    mass_comma = Input.parse_mass("20,5")

    # then
    assert mass == model
    assert mass_comma == model_comma


def test_parsing_mass_out_of_bounds():
    # given
    masses = [0, -5, pow(0.1, MATH_PRECISION + 1)]

    for mass in masses:
        with raises(InputParsingError) as e:
            # when
            Input.parse_mass(str(mass))
            # then
            assert e.value.desc == MSG_OUT_OF_BOUNDS.format("mass", f"(0, inf)", round(mass, MATH_PRECISION))


def test_parsing_velocity():
    # given
    value = 20
    angle = 0.7845
    model = Vector.from_float(cos(angle) * value, sin(angle) * value, UNIT_VELOCITY)

    # when
    velocity = Input.parse_velocity(str(value), Scalar(angle))

    # then
    assert velocity == model


def test_parsing_velocity_out_of_bounds():
    # given
    velocities = [0, -5, pow(0.1, MATH_PRECISION + 1)]

    for vel in velocities:
        with raises(InputParsingError) as e:
            # when
            Input.parse_velocity(str(vel), Scalar(0.5, UNIT_TILT))
            # then
            assert e.value.desc == MSG_OUT_OF_BOUNDS.format("velocity", f"(0, inf)", round(vel, MATH_PRECISION))


def test_parsing_friction():
    # given
    model = Scalar(0.5)
    model_comma = Scalar(0.3)

    # when
    friction = Input.parse_friction("0.5")
    friction_comma = Input.parse_friction("0,3")

    # then
    assert friction == model
    assert friction_comma == model_comma


def test_parsing_friction_out_of_bounds():
    # given
    frictions = [0, -5, pow(0.1, MATH_PRECISION + 1)]

    for f in frictions:
        with raises(InputParsingError) as e:
            # when
            Input.parse_friction(str(f))
            # then
            assert e.value.desc == MSG_OUT_OF_BOUNDS.format("friction", f"(0, inf)", round(f, MATH_PRECISION))
