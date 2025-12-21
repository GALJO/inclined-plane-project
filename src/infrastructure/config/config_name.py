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


class ConfigName(Enum):
    """ """
    port = "port"
    path = "path"

    log = "log"
    level = "level"

    input = "input"
    max_tilt = "max_tilt"
    min_tilt = "min_tilt"
    max_mass = "max_mass"
    min_mass = "min_mass"
    max_velocity = "max_velocity"
    min_velocity = "min_velocity"
    max_friction = "max_friction"
    min_friction = "min_friction"

    output = "output"

    sim = "simulation"
    resolution = "resolution"
    scale = "scale"
    block_size = "block_size"
    fps = "fps"

    math_precision = "math_precision"
    measure_precision = "measure_precision"
    g = "g"

