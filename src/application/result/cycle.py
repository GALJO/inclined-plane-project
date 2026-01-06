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

from pymunk import Vec2d

from application.simulation.model.measurement import Measurement


class Cycle:
    """A class representing a cycle of the simulation.
    One cycle is defined as three Measurements:

    1. The point just after (then bounces off the wall and starts sliding up the plane).\n
    2. The point stops.\n
    3. The point just before collision with the wall (after collision new cycle begin).

    Attributes
    ----------
    number:
        int: Number of the cycle.
    start:
        Measurement: First step of the cycle.
    middle:
        Measurement: Second step of the cycle.
    end:
        Measurement: Third step of the cycle.
    is_full:
        bool: Is cycle full?
    """

    def __init__(self, number: int, start_collision: Measurement, middle_measurement: Measurement,
                 end_collision: Measurement, is_full: bool):
        """
        Class constructor.
        :param number: Number of the cycle.
        :param start_collision: Measurement of the block when ending last cycle (or first ever measurement).
        :param middle_measurement: Measurement of the block when closest to complete stop.
        :param end_collision: Measurement of the block when colliding with the wall.
        """
        self.number: int = number
        self.start: Measurement = start_collision
        self.middle: Measurement = middle_measurement
        self.end: Measurement = end_collision
        self.is_full: bool = is_full

    def __str__(self):
        return f"Cycle(number={self.number} start={self.start} middle={self.middle} end={self.end})"


def collect_cycles(stop_events: list[Measurement], collision_events: list[Measurement], is_full: bool) -> list[Cycle]:
    """Parses simulation's results to simulation's Cycles.

    :param stop_events: list[Measurement]: Stop events measurements.
    :param collision_events: list[Measurement]: Collision events measurements.
    :param is_full: bool: Is cycle full?
    :returns: Simulation's cycles.
    :rtype: list[Cycle]

    """
    logging.debug(f"Collecting cycles.")
    cycles = []
    measurement_ndx = 0
    cycle_n = 1
    for i in range(0, len(collision_events) - 1):
        event = Measurement(-1, Vec2d(1E50, 1E50),
                            Vec2d(1E50, 1E50))
        start = collision_events[i]
        end = collision_events[i + 1]
        while measurement_ndx < len(stop_events) and stop_events[measurement_ndx].time < end.time:
            if stop_events[measurement_ndx].velocity.value < event.velocity.value:
                event = stop_events[measurement_ndx]
            measurement_ndx += 1
        if event.time != -1:
            cycles.append(Cycle(cycle_n, start, event, end, is_full))
            logging.debug(f"Collected cycle: cycle={cycles[-1]}")
            cycle_n += 1
    logging.info(f"Collected cycles: n={len(cycles)}")
    return cycles
