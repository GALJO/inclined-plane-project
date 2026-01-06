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

    def __init__(self, number: int, is_full: bool, duration1: Scalar, duration2: Scalar, start_velocity: Vector,
                 end_velocity: Vector, reach: Vector):
        """
        Class constructor

        Attributes
        ----------
        number: int
        is_full: bool
        duration1: Scalar
        duration2: Scalar
        start_velocity: Vector
        end_velocity: Vector
        reach
        """
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
        """Parses a cycle to readable results.

        :param cycle: Cycle
        :returns: Result.
        :rtype: Result

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
        """Creates model Result using physical formulas.

        :param number: 
        :type number: int
        :param Number of the cycle.: 
        :param start_velocity: 
        :type start_velocity: Vector
        :param Velocity at the 1st point of cycle (meters per second).: 
        :param tilt: Tilt of plane (radians).
        :type tilt: float
        :param f: Coulomb's friction coefficient.
        :type f: float
        :param g: Value of gravitational acceleration (Vector is parallel to Y axis).
        :type g: float
        :param is_full: True if the cycle is full.
        :type is_full: bool
        :param number: int: 
        :param start_velocity: Vector: 
        :param tilt: float: 
        :param f: float: 
        :param g: float: 
        :param is_full: bool: 

        
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
        """
        Converts to string.
        """
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
    """Parses simulation's measurements into readable results.

    :param stop_events: list[Measurement]: Stop events measurements.
    :param collision_events: list[Measurement]: Collision events measurements.
    :param is_full: bool: Is cycle full?
    :returns: List of results.
    :rtype: list[Result]

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
    """Prepares model results based on physics formulas.

    :param inp: Input: The user's input.
    :returns: Results.
    :rtype: list[Result]
    """
    logging.info(f"Calculating model: input={inp}")
    if (inp.friction * cos(inp.tilt.value)) / (sin(inp.tilt.value)) < 1:
        results = [Result.model(0,
                                inp.velocity,
                                inp.tilt.value,
                                inp.friction.value,
                                CONFIG.g,
                                True)]
        logging.debug(f"Calculated model result: n={0} result={results[-1]}")
        i = 1
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
        results = [Result.model(0,
                                inp.velocity,
                                inp.tilt.value,
                                inp.friction.value,
                                CONFIG.g,
                                False)]
        logging.info(f"Not full cycle occurred. result={results[0]}")

    logging.info(f"Calculated model: n={len(results)}")
    return results
