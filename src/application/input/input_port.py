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
from abc import ABC, abstractmethod

from application.input.model.input import Input


class InputPort(ABC):
    """Abstract port responsible for reading input."""

    @abstractmethod
    def get_input(self) -> Input:
        """Reads and parses input from user."""
        pass
