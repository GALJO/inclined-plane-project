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
    # when
    monkeypatch.setattr('builtins.input', lambda _: "0.7")
    inp = adapter.get_input()

    # then
    assert inp.tilt == Scalar(0.7, CONFIG.unit.tilt)
    assert inp.velocity == Vector(Scalar(0.5354, CONFIG.unit.velocity), Scalar(0.451, CONFIG.unit.velocity))
    assert inp.friction == Scalar(0.7)
    assert inp.mass == Scalar(0.7, CONFIG.unit.mass)
