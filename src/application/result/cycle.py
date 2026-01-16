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
    """A class representing a cycle of a simulation.

    One cycle is defined as three Measurement instances:

    1. Measured while collision event (either start of simulation or last cycle's third measurement)

    2. Measured while stop event.

    3. Measured while collision event (may be end of simulation if cycle is not full).

    A cycle is not full only if 3-rd measurement did not happen (is end of simulation).

    Attributes
    ----------
    number:
        (int) Number of the cycle.
    start:
        (Measurement) First of a cycle.
    middle:
        (Measurement) Second of a cycle.
    end:
        (Measurement) Third of a cycle.
    is_full:
        (bool) Is cycle full?
    """

    def __init__(self, number: int, first_measurement: Measurement, second_measurement: Measurement,
                 third_measurement: Measurement, is_full: bool):
        """Constructor.

        :param number: int: Number of the cycle.
        :param first_measurement: Measurement: First measurement.
        :param second_measurement: Measurement: Second measurement.
        :param third_measurement: Measurement: Third measurement.
        :param is_full: bool: Is cycle full?
        """
        self.number: int = number
        self.start: Measurement = first_measurement
        self.middle: Measurement = second_measurement
        self.end: Measurement = third_measurement
        self.is_full: bool = is_full

    def __str__(self):
        return f"Cycle(number={self.number} start={self.start} middle={self.middle} end={self.end})"


def collect_cycles(stop_events: list[Measurement], collision_events: list[Measurement], is_full: bool) -> list[Cycle]:
    """Parses raw Measurements to simulation's Cycles.

    :param stop_events: list[Measurement]: Stop events measurements.
    :param collision_events: list[Measurement]: Collision events measurements.
    :param is_full: bool: Is cycle full?
    :returns: Cycle list.
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
