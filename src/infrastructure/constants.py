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
VERSION = "1.0 BETA"
RESOLUTION = (800, 800)

MATH_PRECISION = 10

UNIT_VELOCITY = "m/s"
UNIT_TILT = "rad"
UNIT_ACCELERATION = "m/s^2"
UNIT_MASS = "kg"
UNIT_DISTANCE = "m"
UNIT_TIME = "s"

SIM_SCALE = 10
SIM_GRAVITY = (0, 9.81 * SIM_SCALE)
SIM_PRECISION = 0.1 * SIM_SCALE
SIM_BLOCK_SIZE = 40
SIM_FPS = 60

OUTPUT_PORT = "CSV"
CSV_PATH = "./output.csv"
LOG_LEVEL = "DEBUG"