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
from application.input.model.input_field import InputField


class InputParsingError(Exception):
    """Exception raised when the input cannot be parsed due to wrong data given by the user.
    Attributes:
        desc: str: Description of the exception.
        field: InputField: Field that exception refers to.
    """
    CODE = "IPE"

    def __init__(self, _desc: str, field: InputField | None):
        self.desc = _desc
        self.field = field

    @classmethod
    def no_field(cls, _desc: str):
        return cls(_desc, None)
