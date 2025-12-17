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
from application.scalar.Scalar import Scalar
from application.math_objects.Vector import translate, translate_abs
from infrastructure.config.Config import RESOLUTION


def test_translation_scalar():
    # given
    x = Scalar(5, "m")
    y = Scalar(6)
    model = (Scalar(5, "m"), Scalar(-6))

    # when then
    assert model == translate(x, y)


def test_translation_number():
    # given
    x = 5
    y = 6
    model = (5, -6)

    # when then
    assert model == translate(x, y)


def test_absolute_translation_scalar():
    # given
    x = Scalar(5, "m")
    y = Scalar(6)
    model = (Scalar(5, "m"), Scalar(-6 + RESOLUTION[1]))

    # when then
    assert model == translate_abs(x, y)


def test_absolute_translation_number():
    # given
    x = 5
    y = 6
    model = (5, -6 + RESOLUTION[1])

    # when then
    assert model == translate_abs(x, y)
