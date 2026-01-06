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


def catcher(f):
    """Wrapper that catches any unhandled exception to log it.

    :param f: Main function.

    """

    def wrap():
        try:
            logging.debug("The Catcher: awaiting disturbance.")
            f()
        except Exception as e:
            logging.critical("The Catcher: unexpected disturbance detected!")
            logging.critical("!!!!!!!!!!!!!!!!!!!!!!!! CRASH !!!!!!!!!!!!!!!!!!!!!!!!")
            logging.critical(e, exc_info=True)
            logging.critical("!!!!!!!!!!!!!!!!!!!!!!!! CRASH !!!!!!!!!!!!!!!!!!!!!!!!")
            raise e

    return wrap
