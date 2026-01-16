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

FORMAT = "[%(asctime)s] [%(levelname)s] || [%(funcName)s] %(filename)s :: %(message)s"


def get_level(level: str):
    """Gets log level.

    :param level: str: Log level in string.

    :returns: Log level readable for logging.
    """
    match level:
        case "DEBUG":
            return logging.DEBUG
        case "INFO":
            return logging.INFO
        case "WARN":
            return logging.WARN
        case "ERROR":
            return logging.ERROR
        case "CRITICAL":
            return logging.CRITICAL
        case _:
            logging.critical("EXIT -- unknown log level.")
            exit(1)
