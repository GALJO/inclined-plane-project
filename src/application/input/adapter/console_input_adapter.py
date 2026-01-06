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

from application.input.exceptions import InputParsingError
from application.input.input_port import InputPort
from application.input.model.input import Input


def handle_error(e: InputParsingError) -> None:
    """Handles InputParsingError.

    :param e: InputParsingError

    """
    print(f"Wrong {e.field.name} field given: {e.desc} ({e.CODE}). Try again.")


def read_console(msg: str):
    """Reads value from console.

    :param msg: Message to user.

    :returns: str: value.

    """
    value = input(msg)
    logging.debug(f"Received value from console: value={value}")
    return value


class ConsoleInputAdapter(InputPort):
    """InputPort adapter responsible for handling console input."""

    def get_input(self) -> Input:
        """Gets input from user using console standard input.

        :returns: Input: Parsed input.
        """
        trial = 0
        while True:
            logging.info(f"Trying to read the input from console: trial_nr={trial}.")
            logging.debug(f"Reading input from console.")
            print("Welcome in the InclinedPlane. Provide constants:")
            print("(You can use multiplies of pi, eg. 0.3p = 0.3 * pi)")
            angle = input("Tilt of plane (rad) (0, 0.5pi) = ")
            logging.debug(f"Received input: angle={angle}")
            friction = input("Friction coefficient (Coulomb friction) (0, inf) = ")
            logging.debug(f"Received input: friction={friction}")
            mass = input("Block's mass (kg) (0, inf) = ")
            logging.debug(f"Received input: mass={mass}")
            velocity = input("Starting velocity (m/s) (parallel to slope) (0, inf) = ")
            logging.debug(f"Received input: velocity={velocity}")
            try:
                inp = Input.user(angle, mass, velocity, friction)
                logging.info(f"Input successfully read: trial_nr={trial} inp={inp}")
                return inp
            except InputParsingError as e:
                logging.error(f"Wrong input provided - retrying: e={e}")
                handle_error(e)
                trial += 1
