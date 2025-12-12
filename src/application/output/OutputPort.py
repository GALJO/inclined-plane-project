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
from abc import abstractmethod, ABC

from application.result.Error import Error
from application.result.Result import Result


class OutputPort(ABC):
    """
    Abstract class that is responsible for output.
    """
    @abstractmethod
    def send_output(self, measured: list[Result], model: list[Result], error: list[Error]) -> None:
        """
        Function that parses output from data and sends it to final location.
        :param measured: List of measured Result objects.
        :param model: List of model Result objects.
        :param error: List of Error objects for each Result object.
        """
        pass
