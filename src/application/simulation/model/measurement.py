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
from pymunk import Vec2d

from application.math.math_util import translate_abs, translate
from application.math.scalar import Scalar
from application.math.vector import Vector
from infrastructure.config.config import CONFIG


class Measurement:
    """A class representing a simulation's measurement.

    It is taken while:

    - A collision event - when the block collides,

    - A stop event - when the block stops moving,

    - A start or an end of a simulation.

    Attributes
    ----------
    time : Scalar
        Timestamp of the measurement.
    position : Vector
        Position of the block.
    velocity : Vector
        Velocity of the block.
    """

    def __init__(self, time: float, position: Vec2d, velocity: Vec2d):
        """Constructor.

        :param time: float: Timestamp of the measurement.
        :param position: pymunk.Vec2d: Position of the block in the simulation.
        :param velocity: pymunk.Vec2d: Velocity of the block in the simulation.
        """
        self.time = Scalar(time, CONFIG.unit.time)
        x, y = translate_abs(position.x, position.y)
        self.position = Vector.from_float(x, y, CONFIG.unit.distance)
        x, y = translate(velocity.x, velocity.y)
        self.velocity = Vector.from_float(x, y, CONFIG.unit.velocity)

    def __str__(self):
        return f"Measurement(time={self.time} position={self.position} velocity={self.velocity})"
