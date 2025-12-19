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
import os
from math import pi
from pathlib import Path

import yaml

from infrastructure.config.ConfigName import ConfigName
from infrastructure.config.InputConfig import InputConfig
from infrastructure.config.UnitConfig import UnitConfig


class Config:
    def __init__(self, math_precision: int,
                 measure_precision: float,
                 log_port: str,
                 log_level: str,
                 log_path: str | None,
                 output_port: str,
                 output_path: str,
                 resolution: tuple[int, int],
                 scale: int,
                 block_size: int,
                 fps: int,
                 g: float,
                 input_config: InputConfig,
                 unit_config: UnitConfig) -> None:
        self.math_precision = math_precision
        self.measure_precision = measure_precision
        self.log_port = log_port
        self.log_level = log_level
        self.log_path = Path(log_path)
        self.output_port = output_port
        self.output_path = Path(output_path)
        self.resolution = resolution
        self.scale = scale
        self.block_size = block_size
        self.fps = fps
        self.g = g
        self.input = input_config
        self.unit = unit_config

    @classmethod
    def default(cls):
        math_precision = 10
        inp: InputConfig = InputConfig("CONSOLE",
                                       0,
                                       0,
                                       0,
                                       0,
                                       0.5 * pi,
                                       None,
                                       None,
                                       None,
                                       math_precision)
        config = cls(math_precision,
                     0.1,
                     "FILE",
                     "DEBUG",
                     "./log/log.log",
                     "CSV",
                     "./output.csv",
                     (800, 800),
                     10,
                     40,
                     60,
                     9.81,
                     inp,
                     UnitConfig())
        logging.debug(f"Default config loaded: config={config}")
        return config

    def generate_file(self, path: Path) -> None:
        logging.debug(f"Generating a default config file: path={path}")
        struct = {}
        struct.setdefault(ConfigName.log.value, {})
        struct[ConfigName.log.value].setdefault(ConfigName.port.value, self.log_port)
        struct[ConfigName.log.value].setdefault(ConfigName.level.value, self.log_level)
        struct[ConfigName.log.value].setdefault(ConfigName.path.value, self.log_path.__str__())

        struct.setdefault(ConfigName.input.value, {})
        struct[ConfigName.input.value].setdefault(ConfigName.port.value, self.input.port)
        struct[ConfigName.input.value].setdefault(ConfigName.max_tilt.value, self.input.max_tilt)
        struct[ConfigName.input.value].setdefault(ConfigName.max_mass.value, self.input.max_mass)
        struct[ConfigName.input.value].setdefault(ConfigName.max_velocity.value, self.input.max_velocity)
        struct[ConfigName.input.value].setdefault(ConfigName.max_friction.value, self.input.max_friction)
        struct[ConfigName.input.value].setdefault(ConfigName.min_tilt.value, self.input.min_tilt)
        struct[ConfigName.input.value].setdefault(ConfigName.min_mass.value, self.input.min_mass)
        struct[ConfigName.input.value].setdefault(ConfigName.min_velocity.value, self.input.min_velocity)
        struct[ConfigName.input.value].setdefault(ConfigName.min_friction.value, self.input.min_friction)

        struct.setdefault(ConfigName.output.value, {})
        struct[ConfigName.output.value].setdefault(ConfigName.port.value, self.output_port)
        struct[ConfigName.output.value].setdefault(ConfigName.path.value, self.output_path.__str__())

        struct.setdefault(ConfigName.sim.value, {})
        struct[ConfigName.sim.value].setdefault(ConfigName.resolution.value,
                                                [self.resolution[0], self.resolution[1]])
        struct[ConfigName.sim.value].setdefault(ConfigName.scale.value, self.scale)
        struct[ConfigName.sim.value].setdefault(ConfigName.block_size.value, self.block_size)
        struct[ConfigName.sim.value].setdefault(ConfigName.fps.value, self.fps)

        struct.setdefault(ConfigName.math_precision.value, self.math_precision)
        struct.setdefault(ConfigName.measure_precision.value, self.measure_precision)
        struct.setdefault(ConfigName.g.value, self.g)
        os.makedirs(os.path.dirname(path.absolute()), exist_ok=True)
        with open(path.absolute(), "w") as conf:
            yaml.dump(struct, conf)
        logging.debug(f"Generated a default config file: insides={struct}")

    def update(self, path: Path):
        logging.info(f"Loading the config from a file: path={path.absolute()}")
        if not path.exists():
            logging.warning(f"A config file does not exists; generating a new one: path={path.absolute()}")
            self.generate_file(path)
        with open(path, "r") as conf:
            config = yaml.safe_load(conf)
            self.math_precision = get_value(config, ConfigName.math_precision)
            self.measure_precision = get_value(config, ConfigName.measure_precision)
            self.log_port = get_value(config, ConfigName.log, ConfigName.port)
            self.log_path = Path(get_value(config, ConfigName.log, ConfigName.path))
            self.log_level = get_value(config, ConfigName.log, ConfigName.level)
            self.output_path = Path(get_value(config, ConfigName.output, ConfigName.path))
            self.output_port = get_value(config, ConfigName.output, ConfigName.port)
            self.resolution = tuple(get_value(config, ConfigName.sim, ConfigName.resolution))
            self.scale = get_value(config, ConfigName.sim, ConfigName.scale)
            self.block_size = get_value(config, ConfigName.sim, ConfigName.block_size)
            self.fps = get_value(config, ConfigName.sim, ConfigName.fps)
            self.g = get_value(config, ConfigName.g)
            self.input = InputConfig(get_value(config, ConfigName.input, ConfigName.port),
                                     get_value(config, ConfigName.input, ConfigName.min_tilt),
                                     get_value(config, ConfigName.input, ConfigName.min_mass),
                                     get_value(config, ConfigName.input, ConfigName.min_velocity),
                                     get_value(config, ConfigName.input, ConfigName.min_friction),
                                     get_value(config, ConfigName.input, ConfigName.max_tilt),
                                     get_value(config, ConfigName.input, ConfigName.max_mass),
                                     get_value(config, ConfigName.input, ConfigName.max_velocity),
                                     get_value(config, ConfigName.input, ConfigName.max_friction),
                                     self.math_precision)

        logging.info(f"Updated the config.")


def get_value(config: dict, *names: ConfigName):
    value = config
    log_name = ""
    for name in names:
        value = value[name.value]
        log_name += name.value + "."
    logging.debug(f"From config file: {log_name[:-1]}={value}")
    return value


CONFIG = Config.default()
