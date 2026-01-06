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
    """A class representing a measurement in simulation.
    It stores data about time of measurement and block parameters.
    It can be one of two simulation events:\n
    - Complete stop of the block,\n
    - Collision between the wall and the block.


    Attributes
    ----------
    time : Scalar
        Timestamp of the measurement.
    position : Vector
        Measured position of the block.
    velocity : Vector
        Measured velocity of the block.
    """

    def __init__(self, _time: float, _position: Vec2d, _velocity: Vec2d):
        """
        Class constructor.
        Parameters
        ----------
        _time: float
            Timestamp of the measurement.
        _position: Vec2d
            Measured position of the block (Vec2d pymunk object)
        _velocity: Vec2d
            Measured velocity of the block (Vec2d pymunk object)
        """
        self.time = Scalar(_time, CONFIG.unit.time)
        x, y = translate_abs(_position.x, _position.y)
        self.position = Vector.from_float(x, y, CONFIG.unit.distance)
        x, y = translate(_velocity.x, _velocity.y)
        self.velocity = Vector.from_float(x, y, CONFIG.unit.velocity)

    def __str__(self):
        """
        Converts to string.
        """
        return f"Measurement(time={self.time} position={self.position} velocity={self.velocity})"
