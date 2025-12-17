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
from pathlib import Path

import yaml

from infrastructure.config.config import *


class Config:
    def __init__(self, config_path: Path):
        self.path = config_path.absolute()

    def generate_file(self) -> None:
        logging.debug(f"Generating a config file")
        struct = {}
        struct.setdefault(ConfigNames.LOG.value, {})
        struct[ConfigNames.LOG.value].setdefault(ConfigNames.PORT.value, LOG_PORT)
        struct[ConfigNames.LOG.value].setdefault(ConfigNames.LOG_LEVEL.value, LOG_LEVEL)
        struct[ConfigNames.LOG.value].setdefault(ConfigNames.PATH.value, LOG_PATH)

        struct.setdefault(ConfigNames.INPUT.value, {})
        struct[ConfigNames.INPUT.value].setdefault(ConfigNames.PORT.value, INPUT_PORT)
        struct[ConfigNames.INPUT.value].setdefault(ConfigNames.MAX_TILT.value, MAX_TILT)
        struct[ConfigNames.INPUT.value].setdefault(ConfigNames.MAX_MASS.value, MAX_MASS)
        struct[ConfigNames.INPUT.value].setdefault(ConfigNames.MAX_VELOCITY.value, MAX_VELOCITY)
        struct[ConfigNames.INPUT.value].setdefault(ConfigNames.MAX_FRICTION.value, MAX_FRICTION)
        struct[ConfigNames.INPUT.value].setdefault(ConfigNames.MIN_TILT.value, MIN_TILT)
        struct[ConfigNames.INPUT.value].setdefault(ConfigNames.MIN_MASS.value, MIN_MASS)
        struct[ConfigNames.INPUT.value].setdefault(ConfigNames.MIN_VELOCITY.value, MIN_VELOCITY)
        struct[ConfigNames.INPUT.value].setdefault(ConfigNames.MIN_FRICTION.value, MIN_FRICTION)

        struct.setdefault(ConfigNames.OUTPUT.value, {})
        struct[ConfigNames.OUTPUT.value].setdefault(ConfigNames.PORT.value, OUTPUT_PORT)
        struct[ConfigNames.OUTPUT.value].setdefault(ConfigNames.PATH.value, OUTPUT_PATH)

        struct.setdefault(ConfigNames.SIM.value, {})
        struct[ConfigNames.SIM.value].setdefault(ConfigNames.SIM_RESOLUTION.value,
                                                 [SIM_RESOLUTION[0], SIM_RESOLUTION[1]])
        struct[ConfigNames.SIM.value].setdefault(ConfigNames.SIM_SCALE.value, SIM_SCALE)
        struct[ConfigNames.SIM.value].setdefault(ConfigNames.SIM_BLOCK_SIZE.value, SIM_BLOCK_SIZE)
        struct[ConfigNames.SIM.value].setdefault(ConfigNames.SIM_FPS.value, SIM_FPS)

        struct.setdefault(ConfigNames.MATH_PRECISION.value, MATH_PRECISION)
        struct.setdefault(ConfigNames.MEASURE_PRECISION.value, MEASURE_PRECISION)
        struct.setdefault(ConfigNames.G.value, G)

        with open(self.path, "w") as conf:
            yaml.dump(struct, conf)
        logging.debug(f"Generated a config file: path={self.path} insides={struct}")

    def set(self) -> None:
        logging.info(f"Setting up config from file: path={self.path}")
        if not Path.exists(self.path):
            logging.warning(f"The config file do not exist; generating new default one: path={self.path}")
            self.generate_file()
        with open(self.path, "r") as conf:
            config = yaml.safe_load(conf)
            logging.debug(f"Loaded config file: config={config}")
            set_global_variables(config)
        logging.info(f"Set up config.")
