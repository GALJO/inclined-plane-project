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
import pytest

from application.input.adapter.console_input_adapter import ConsoleInputAdapter
from application.math.scalar import Scalar
from application.math.vector import Vector
from infrastructure.config.config import CONFIG


@pytest.fixture
def adapter() -> ConsoleInputAdapter:
    return ConsoleInputAdapter()


# POSITIVE
def test_reading_console(adapter: ConsoleInputAdapter, monkeypatch):
    # given
    velocity_model = Vector(Scalar(0.5354, CONFIG.unit.velocity), Scalar(0.451, CONFIG.unit.velocity))

    # when
    monkeypatch.setattr('builtins.input', lambda _: "0.7")
    inp = adapter.get_input()

    # then
    assert inp.tilt == Scalar(0.7, CONFIG.unit.tilt)
    assert inp.velocity.x == velocity_model.x
    assert inp.velocity.y == velocity_model.y
    assert inp.velocity.value == velocity_model.value
    assert inp.friction == Scalar(0.7)
    assert inp.mass == Scalar(0.7, CONFIG.unit.mass)
