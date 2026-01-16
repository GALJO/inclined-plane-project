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
from math import sin, cos, sqrt

from application.input.model.input import Input
from application.math.scalar import Scalar
from application.math.vector import Vector
from application.result.cycle import Cycle, collect_cycles
from application.simulation.model.measurement import Measurement
from infrastructure.config.config import CONFIG


class Result:
    """A class containing Result for one cycle.

    Attributes
    ----------
    number
        (int) Number of the cycle.
    is_full
        (bool) Is the cycle full?
    duration1
        (Scalar) A duration from first to second measurement of the cycle.
    duration2
        (Scalar) A duration from second to third measurement of the cycle.
    start_velocity
        (Vector) A velocity in first measurement of the cycle.
    end_velocity
        (Vector) A velocity in third measurement of the cycle.
    reach
        (Vector) A distance between first and second measurement's position.
    """

    def __init__(self, number: int, is_full: bool, duration1: Scalar, duration2: Scalar, start_velocity: Vector,
                 end_velocity: Vector, reach: Vector):
        """Class constructor"""
        self.number = number
        self.is_full = is_full
        self.duration1 = duration1
        self.duration2 = duration2
        self.duration = duration1 + duration2 if is_full else duration1
        self.start_velocity = abs(start_velocity)
        self.end_velocity = end_velocity
        self.reach = reach

    @classmethod
    def measured(cls, cycle: Cycle):
        """Returns a Result parsed from a Cycle instance.

        :param cycle: Cycle
        """
        return cls(cycle.number,
                   cycle.is_full,
                   cycle.middle.time - cycle.start.time,
                   cycle.end.time - cycle.middle.time if cycle.is_full else Scalar.nan(),
                   Vector(abs(cycle.start.velocity.x / CONFIG.scale),
                          abs(cycle.start.velocity.y / CONFIG.scale)),
                   Vector(cycle.end.velocity.x / CONFIG.scale, cycle.end.velocity.y / CONFIG.scale),
                   Vector(abs(cycle.start.position.x - cycle.middle.position.x) / CONFIG.scale,
                          abs(cycle.start.position.y - cycle.middle.position.y) / CONFIG.scale))

    @classmethod
    def model(cls, number: int, start_velocity: Vector, tilt: float, f: float, g: float, is_full: bool):
        """Returns Result computed using given data and physics formulas.

        :param number: int: Number of the cycle.
        :param start_velocity: Vector: Starting velocity of the cycle.
        :param tilt: Tilt angle.
        :param f: Friction coefficient.
        :param g: Gravitational acceleration.
        :param is_full: Is cycle full?
        """
        v0 = start_velocity.value.value
        reach_value = (v0 * v0) / (2 * g * (f * cos(tilt) + sin(tilt)))

        if not is_full:
            end_velocity = Vector.from_float(0, 0, CONFIG.unit.velocity)
        else:
            v1 = v0 * sqrt((sin(tilt) - f * cos(tilt)) / (sin(tilt) + f * cos(tilt)))
            end_velocity = Vector.from_float(-cos(tilt) * v1, -sin(tilt) * v1,
                                             CONFIG.unit.velocity)

        d1 = Scalar(v0 / (g * (sin(tilt) + f * cos(tilt))), CONFIG.unit.time)
        d2 = Scalar(end_velocity.value.value / (g * (sin(tilt) - f * cos(tilt))), CONFIG.unit.time)

        reach = Vector.from_float(cos(tilt) * reach_value, sin(tilt) * reach_value, CONFIG.unit.distance)

        return cls(number, is_full, d1, d2 if is_full else Scalar.nan(), start_velocity, end_velocity, reach)

    def __str__(self):
        return (f"Result(number={self.number} "
                f"is_full={self.is_full} "
                f"duration1={self.duration1} "
                f"duration2={self.duration2} "
                f"duration={self.duration} "
                f"start_velocity={self.start_velocity} "
                f"end_velocity={self.end_velocity} "
                f"reach={self.reach})")


def prepare_simulation_results(stop_events: list[Measurement], collision_events: list[Measurement], is_full: bool) \
        -> list[Result]:
    """Parses a simulation's measurements into Results.

    :param stop_events: list[Measurement]: Stop events measurements.
    :param collision_events: list[Measurement]: Collision events measurements.
    :param is_full: bool: Is cycle full?

    :returns: List of Results.
    """
    logging.info(f"Preparing simulation results: is_full={is_full}")
    results = []
    cycles = collect_cycles(stop_events, collision_events, is_full)
    for cycle in cycles:
        results.append(Result.measured(cycle))
        logging.debug(f"Prepared result: result={results[-1]} cycle={cycle}")
    logging.info(f"Prepared simulation results: n={len(results)}")
    return results


def calculate_theoretical_model(inp: Input) -> list[Result]:
    """Prepares model results.

    :param inp: Input: The user's input.

    :returns: List of Results.
    """
    logging.info(f"Calculating model: input={inp}")
    if (inp.friction * cos(inp.tilt.value)) / (sin(inp.tilt.value)) < 1:
        results = [Result.model(1,
                                inp.velocity,
                                inp.tilt.value,
                                inp.friction.value,
                                CONFIG.g,
                                True)]
        logging.debug(f"Calculated model result: n={0} result={results[-1]}")
        i = 2
        while results[-1].end_velocity.value > CONFIG.measure_precision:
            results.append(Result.model(i,
                                        results[-1].end_velocity,
                                        inp.tilt.value,
                                        inp.friction.value,
                                        CONFIG.g,
                                        True))
            logging.debug(f"Calculated model result: n={i} result={results[-1]}")
            i += 1
    else:
        results = [Result.model(1,
                                inp.velocity,
                                inp.tilt.value,
                                inp.friction.value,
                                CONFIG.g,
                                False)]
        logging.info(f"Not full cycle occurred. result={results[0]}")

    logging.info(f"Calculated model: n={len(results)}")
    return results
