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
from math import pi

RESOLUTION = (800, 800)
LOG_LEVEL = "DEBUG"

MATH_PRECISION = 10

G_ACCELERATION = 9.81

UNIT_VELOCITY = "m/s"
UNIT_TILT = "rad"
UNIT_ACCELERATION = "m/s^2"
UNIT_MASS = "kg"
UNIT_DISTANCE = "m"
UNIT_TIME = "s"

TILT_MIN = 0
TILT_MAX = round(0.5 * pi, MATH_PRECISION)
MASS_MIN = 0
MASS_MAX = None
VELOCITY_MIN = 0
VELOCITY_MAX = None
FRICTION_MIN = 0
FRICTION_MAX = None

SIM_SCALE = 10
SIM_PRECISION = 0.1 * SIM_SCALE
SIM_BLOCK_SIZE = 40
SIM_FPS = 60

OUTPUT_PORT = "CSV"
OUTPUT_CSV_PATH = "./output.csv"
