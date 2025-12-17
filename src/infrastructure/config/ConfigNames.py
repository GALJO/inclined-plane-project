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
from enum import Enum


class ConfigNames(Enum):
    PORT = "port"
    PATH = "path"

    LOG = "log"
    LOG_LEVEL = "level"

    INPUT = "input"
    MAX_TILT = "max_tilt"
    MIN_TILT = "min_tilt"
    MAX_MASS = "max_mass"
    MIN_MASS = "min_mass"
    MAX_VELOCITY = "max_velocity"
    MIN_VELOCITY = "min_velocity"
    MAX_FRICTION = "max_friction"
    MIN_FRICTION = "min_friction"

    OUTPUT = "output"

    SIM = "simulation"
    SIM_RESOLUTION = "resolution"
    SIM_SCALE = "scale"
    SIM_BLOCK_SIZE = "block_size"
    SIM_FPS = "fps"

    MATH_PRECISION = "math_precision"
    MEASURE_PRECISION = "measure_precision"

    G = "g"