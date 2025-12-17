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
from math import pi

from infrastructure.config.ConfigNames import ConfigNames

# Logger config.
LOG_PORT: str = "FILE"
LOG_LEVEL: str = "DEBUG"
LOG_PATH: str | None = "./log.log"

# Input config.
INPUT_PORT: str = "CONSOLE"

MIN_TILT: float | None = 0
MIN_MASS: float | None = 0
MIN_VELOCITY: float | None = 0
MIN_FRICTION: float | None = 0

MAX_TILT: float | None = round(0.5 * pi, 10)
MAX_MASS: float | None = None
MAX_VELOCITY: float | None = None
MAX_FRICTION: float | None = None

# Output config.
OUTPUT_PORT: str = "CSV"
OUTPUT_PATH: str = "./output.csv"

# Simulation config.
SIM_RESOLUTION: tuple[int, int] = (800, 800)
SIM_SCALE: int = 10
SIM_BLOCK_SIZE: int = 40
SIM_FPS: int = 60

# Precision config.
MATH_PRECISION: int = 10
MEASURE_PRECISION: float = 0.1

# Gravity acceleration.
G: float = 9.81

# Unit config.
UNIT_DISTANCE: str = "m"
UNIT_TIME: str = "s"
UNIT_TILT: str = "rad"
UNIT_MASS: str = "kg"
UNIT_VELOCITY: str = f"{UNIT_DISTANCE}/{UNIT_TIME}"
UNIT_ACCELERATION: str = f"{UNIT_DISTANCE}/{UNIT_TIME}^2"


def log_variable_set(name: str, value) -> None:
    logging.debug(f"Set {name} to {value}")


def set_global_variables(config: dict):
    logging.debug(f"Setting global config variables: config={config}")
    global LOG_PORT, LOG_LEVEL, LOG_PATH
    global INPUT_PORT, MIN_TILT, MIN_MASS, MIN_VELOCITY, MIN_FRICTION
    global MAX_TILT, MAX_MASS, MAX_VELOCITY, MAX_FRICTION
    global OUTPUT_PORT, OUTPUT_PATH
    global SIM_RESOLUTION, SIM_SCALE, SIM_BLOCK_SIZE, SIM_FPS
    global MATH_PRECISION, MEASURE_PRECISION, G

    LOG_PORT = config[ConfigNames.LOG.value][ConfigNames.PORT.value]
    log_variable_set(f"{ConfigNames.LOG.name}_{ConfigNames.PORT.name}", LOG_PORT)
    LOG_LEVEL = config[ConfigNames.LOG.value][ConfigNames.LOG_LEVEL.value]
    log_variable_set(ConfigNames.LOG_LEVEL.name, LOG_LEVEL)
    LOG_PATH = config[ConfigNames.LOG.value][ConfigNames.PATH.value]
    log_variable_set(f"{ConfigNames.LOG.name}_{ConfigNames.PATH.name}", LOG_PATH)

    INPUT_PORT = config[ConfigNames.INPUT.value][ConfigNames.PORT.value]
    log_variable_set(f"{ConfigNames.INPUT.name}_{ConfigNames.PORT.name}", INPUT_PORT)

    MIN_TILT = config[ConfigNames.INPUT.value][ConfigNames.MIN_TILT.value]
    log_variable_set(ConfigNames.MIN_TILT.name, MIN_TILT)
    MIN_MASS = config[ConfigNames.INPUT.value][ConfigNames.MIN_MASS.value]
    log_variable_set(ConfigNames.MIN_MASS.name, MIN_MASS)
    MIN_VELOCITY = config[ConfigNames.INPUT.value][ConfigNames.MIN_VELOCITY.value]
    log_variable_set(ConfigNames.MIN_VELOCITY.name, MIN_VELOCITY)
    MIN_FRICTION = config[ConfigNames.INPUT.value][ConfigNames.MIN_FRICTION.value]
    log_variable_set(ConfigNames.MIN_FRICTION.name, MIN_FRICTION)

    MAX_TILT = config[ConfigNames.INPUT.value][ConfigNames.MAX_TILT.value]
    log_variable_set(ConfigNames.MAX_TILT.name, MAX_TILT)
    MAX_MASS = config[ConfigNames.INPUT.value][ConfigNames.MAX_MASS.value]
    log_variable_set(ConfigNames.MAX_MASS.name, MAX_MASS)
    MAX_VELOCITY = config[ConfigNames.INPUT.value][ConfigNames.MAX_VELOCITY.value]
    log_variable_set(ConfigNames.MAX_VELOCITY.name, MAX_VELOCITY)
    MAX_FRICTION = config[ConfigNames.INPUT.value][ConfigNames.MAX_FRICTION.value]
    log_variable_set(ConfigNames.MAX_FRICTION.name, MAX_FRICTION)

    SIM_RESOLUTION = (config[ConfigNames.SIM.value][ConfigNames.SIM_RESOLUTION.value][0],
                      config[ConfigNames.SIM.value][ConfigNames.SIM_RESOLUTION.value][1])
    log_variable_set(ConfigNames.SIM_RESOLUTION.name, SIM_RESOLUTION)
    SIM_SCALE = config[ConfigNames.SIM.value][ConfigNames.SIM_SCALE.value]
    log_variable_set(ConfigNames.SIM_SCALE.name, SIM_SCALE)
    SIM_BLOCK_SIZE = config[ConfigNames.SIM.value][ConfigNames.SIM_BLOCK_SIZE.value]
    log_variable_set(ConfigNames.SIM_BLOCK_SIZE.name, SIM_BLOCK_SIZE)
    SIM_FPS = config[ConfigNames.SIM.value][ConfigNames.SIM_FPS.value]
    log_variable_set(ConfigNames.SIM_FPS.name, SIM_FPS)

    MATH_PRECISION = config[ConfigNames.MATH_PRECISION.value]
    log_variable_set(ConfigNames.MATH_PRECISION.name, MATH_PRECISION)
    MEASURE_PRECISION = config[ConfigNames.MEASURE_PRECISION.value]
    log_variable_set(ConfigNames.MEASURE_PRECISION.name, MEASURE_PRECISION)
    G = config[ConfigNames.G.value]
    log_variable_set(ConfigNames.G.name, G)
    logging.debug("Set global variables.")
