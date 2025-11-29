import sys
from math import sin, cos, tan, radians, sqrt, degrees
from time import time

import pygame
import pymunk.pygame_util
from pymunk import Arbiter, Space, Vec2d, Body

VERSION = "1.0 BETA"
RESOLUTION = (800, 800)

D = 1e-10

UNIT_VELOCITY = "m/s"
UNIT_ACCELERATION = "m/s^2"
UNIT_MASS = "kg"
UNIT_DISTANCE = "m"
UNIT_TIME = "s"


def translate_abs(x: float, y: float):
    return x, RESOLUTION[1] - y


def translate(x: float, y: float):
    return x, -y


def time_str(t) -> str:
    return f"{t}{UNIT_TIME}"


class Vector:
    def __init__(self, _x: float, _y: float, _unit: str):
        self.x = 0 if abs(_x) < D else _x
        self.y = 0 if abs(_y) < D else _y
        self.value = sqrt(self.x ** 2 + self.y ** 2)
        self.unit = _unit

    def translated(self) -> tuple[float, float]:
        return translate(self.x, self.y)

    def translated_abs(self) -> tuple[float, float]:
        return translate_abs(self.x, self.y)

    def __str__(self):
        return f"[{self.x}{self.unit}, {self.y}{self.unit}]"

    def str_translated(self) -> str:
        x, y = self.translated()
        return f"[{x}{self.unit}, {y}{self.unit}]"

    def str_abs(self) -> str:
        x, y = self.translated_abs()
        return f"[{x}{self.unit}, {y}{self.unit}]"

    def str_value(self) -> str:
        return f"{self.value}{self.unit}"

    def __mul__(self, other: int | float):
        return Vector(self.x * other, self.y * other, self.unit)


class Input:
    @staticmethod
    def verify_input(tilt: float, mass: float, velocity: float, friction: float):
        pass

    def __init__(self, _tilt: float, _mass: float, _velocity: float, _friction: float, _scale: int):
        self.verify_input(_tilt, _mass, _velocity, _friction)

        self.tilt = _tilt
        self.mass_u = _mass
        self.velocity_u = Vector(_velocity * cos(_tilt), _velocity * sin(_tilt), UNIT_VELOCITY)
        self.mass = _mass * _scale
        self.velocity = Vector(self.velocity_u.x * _scale, self.velocity_u.y * _scale, UNIT_VELOCITY)
        self.friction = _friction

    def pretty_str(self):
        return f"Input data:\n" \
               f"Slope angle = {self.tilt} rad (= {degrees(self.tilt)} degrees)\n" \
               f"Start velocity vector (parallel to slope) = {self.velocity_u} ({self.velocity_u.str_value()})\n" \
               f"Mass of the block* = {self.mass_u}{UNIT_MASS}\n" \
               f"Dynamic friction coefficient between block and slope (Coulomb friction model) = {self.friction}\n"

    def to_str_usr(self) -> str:
        return (f"User Input: "
                f"tilt={self.tilt} "
                f"mass={self.mass_u} "
                f"velocity={self.velocity_u} "
                f"friction={self.friction}")

    def __str__(self):
        return (f"Input: "
                f"tilt={self.tilt} "
                f"mass={self.mass} "
                f"velocity={self.velocity} ({self.velocity.str_translated()})"
                f"friction={self.friction}")


class Settings:
    def __init__(self, _scale: int, _gravity: Vector, _resolution: tuple[int, int], _block_size: int, _precision: float,
                 _fps: int):
        self.scale = _scale
        self.gravity = _gravity * _scale
        self.resolution = _resolution
        self.block_size = _block_size
        self.precision = _precision * _scale
        self.fps = _fps

    def __str__(self):
        return (
            f"Settings: scale={self.scale} gravity={self.gravity} "
            f"resolution=({self.resolution[0]}, {self.resolution[1]}) fps={self.fps}")


class Measurement:
    def __init__(self, _time: float, _position: Vec2d, _velocity: Vec2d):
        self.time = 0 if abs(_time) < D else _time
        x, y = translate_abs(_position.x, _position.y)
        self.position = Vector(x, y, UNIT_DISTANCE)
        x, y = translate(_velocity.x, _velocity.y)
        self.velocity = Vector(x, y, UNIT_VELOCITY)

    def __str__(self):
        return f"Measurement(time={self.time}, position={self.position}, velocity={self.velocity})"

    def to_str_stop(self) -> str:
        return (f"[{self.time}] Block stop detection. "
                f"pos={self.position.str_abs()} vel={self.velocity.str_translated()}")

    def to_str_col(self) -> str:
        return (f"[{self.time}] Block-wall collision. "
                f"pos={self.position.str_abs()} "
                f"vel={self.velocity.str_translated()}")


class Cycle:
    def __init__(self, _number: int, _start_collision: Measurement, _middle_measurement: Measurement,
                 _end_collision: Measurement):
        self.number = _number
        self.start = _start_collision
        self.middle = _middle_measurement
        self.end = _end_collision


class ResultMeasured:
    def __init__(self, cycle: Cycle, scale: int, is_full: bool):
        self.number = cycle.number
        self.is_full = is_full
        self.duration1 = cycle.middle.time - cycle.start.time

        if not is_full:
            self.duration2 = -1
        else:
            self.duration2 = cycle.end.time - cycle.middle.time
        self.start_velocity = Vector(abs(cycle.start.velocity.x / scale), abs(cycle.start.velocity.y / scale),
                                     UNIT_VELOCITY)
        self.end_velocity = Vector(cycle.end.velocity.x / scale, cycle.end.velocity.y / scale, UNIT_VELOCITY)
        # start -> middle distance
        self.reach = Vector(abs(cycle.start.position.x - cycle.middle.position.x) / scale,
                            abs(cycle.start.position.y - cycle.middle.position.y) / scale, UNIT_DISTANCE)


class ResultModel:
    def __init__(self, _cycle_n: int, _start_velocity: Vector, _tilt: float, _fr: float, _g: float, _is_full: bool):
        v1 = _start_velocity.value
        reach_value = (v1 ** 2) / (2 * _g * (_fr * cos(_tilt) + sin(_tilt)))
        end_velocity_co = (2 * tan(_tilt) - _fr) / (2 * (_fr + tan(_tilt)))

        self.number = _cycle_n
        self.is_full = _is_full

        self.start_velocity = _start_velocity
        if not _is_full:
            self.end_velocity = Vector(0, 0, UNIT_VELOCITY)
        else:
            end_velocity_co = v1 * sqrt(end_velocity_co)
            self.end_velocity = Vector(-cos(_tilt) * end_velocity_co, -sin(_tilt) * end_velocity_co, UNIT_VELOCITY)

        self.duration1 = v1 / (_g * (sin(_tilt) + _fr * cos(_tilt)))
        if not _is_full:
            self.duration2 = -1
        else:
            self.duration2 = self.end_velocity.value / (_g * (sin(_tilt) - _fr * cos(_tilt)))

        self.reach = Vector(cos(_tilt) * reach_value, sin(_tilt) * reach_value, UNIT_DISTANCE)


class Error:
    @staticmethod
    def vector_error(vec: Vector, vec0: Vector) -> Vector:
        return Vector(abs(vec.x - vec0.x), abs(vec.y - vec0.y), vec.unit)

    @staticmethod
    def scalar_error(x: float, x0: float) -> float:
        return abs(x - x0)

    @staticmethod
    def vector_relative_error(e: Vector, v: Vector) -> tuple[float, float]:
        return e.x / v.x if v.x != 0 else float("NaN"), e.y / v.y if v.y != 0 else float("NaN")

    @staticmethod
    def vector_val_relative_error(e: Vector, v: Vector) -> float:
        return e.value / v.value if v.value != 0 else float("NaN")

    @staticmethod
    def scalar_relative_error(e: float, v: float) -> float:
        return e / v if v != 0 else float("NaN")

    def __init__(self, measure: ResultMeasured, model: ResultModel):
        self.duration1 = self.scalar_error(model.duration1, measure.duration1)
        self.duration1_rel = self.scalar_relative_error(self.duration1, measure.duration1)
        self.duration2 = self.scalar_error(model.duration2, measure.duration2)
        self.duration2_rel = self.scalar_relative_error(self.duration2, measure.duration2)

        if measure.is_full:
            self.duration = self.duration1
            self.duration_rel = self.duration1_rel
        else:
            self.duration = self.scalar_error(model.duration1 + model.duration2, measure.duration1 + measure.duration2)
            self.duration_rel = self.scalar_relative_error(self.duration, measure.duration1 + measure.duration2)

        self.start_velocity = self.vector_error(model.start_velocity, measure.start_velocity)
        self.start_velocity_rel = self.vector_relative_error(self.start_velocity, measure.start_velocity)
        self.start_velocity_value_rel = self.vector_val_relative_error(self.start_velocity, measure.start_velocity)

        self.end_velocity = self.vector_error(model.end_velocity, measure.end_velocity)
        self.end_velocity_rel = self.vector_relative_error(self.end_velocity, measure.end_velocity)
        self.end_velocity_value_rel = self.vector_val_relative_error(self.end_velocity, measure.end_velocity)

        self.reach = self.vector_error(model.reach, measure.reach)
        self.reach_rel = self.vector_relative_error(self.reach, measure.reach)
        self.reach_value_rel = self.vector_val_relative_error(self.reach, measure.reach)


def init_space(inp: Input, settings: Settings) -> tuple[Space, Body]:
    print("Initializing space.")
    space = pymunk.Space()
    space.gravity = settings.gravity.translated()

    plane = pymunk.Segment(space.static_body, translate_abs(50, 0),
                           translate_abs(5000, tan(inp.tilt) * 5000), 4)
    plane.friction = 1

    wall = pymunk.Segment(space.static_body, translate_abs(100, 0),
                          translate_abs(0, (100 / tan(inp.tilt))), 4)
    wall.elasticity = 1
    wall.collision_type = 1

    block_body = pymunk.Body(mass=inp.mass,
                             moment=pymunk.moment_for_box(sys.float_info.max,
                                                          (settings.block_size, settings.block_size)))
    block_body.angle = radians(270) - inp.tilt
    block_body.position = translate_abs(100 - 50 * sin(inp.tilt) ** 2, 50 * sin(inp.tilt) * cos(inp.tilt))

    block = pymunk.Poly(block_body, [(0, 0), (0, settings.block_size),
                                     (settings.block_size, 0), (settings.block_size, settings.block_size)])
    block.elasticity = 1
    block.friction = inp.friction
    block.collision_type = 1

    space.add(block_body, block, plane, wall)
    print(f"Initialized space. gravity={space.gravity}")
    return space, block_body


def handle_block_wall_collision(arbiter: Arbiter, space: Space, data: list[Measurement]) -> None:
    data.append(Measurement(round(time(), 2), arbiter.shapes[1].body.position, arbiter.shapes[1].body.velocity))
    print(data[-1].to_str_col())


def simulate(space: Space, block: Body, inp: Input, settings: Settings, model_cycles_amount: int, is_cycle: bool) -> \
        tuple[list[Measurement], list[Measurement], float]:
    display = pygame.display.set_mode(settings.resolution)
    draw_options = pymunk.pygame_util.DrawOptions(display)
    clock = pygame.time.Clock()

    vx, vy = inp.velocity.translated()
    block.apply_impulse_at_world_point((vx * inp.mass, vy * inp.mass), translate_abs(0, 0))

    collisions: list[Measurement] = []
    measurements: list[Measurement] = []
    space.on_collision(
        1,
        1,
        handle_block_wall_collision,
        None,
        None,
        None,
        data=collisions
    )

    pygame.init()

    print("--SIMULATION START--")
    start_time = round(time(), 2)
    start_measurement = Measurement(start_time, block.position, block.velocity)
    print(f"start_time={start_time} "
          f"start_measurement={start_measurement} "
          f"start_pos=[{block.position.x}, {block.position.y}] "
          f"start_velocity=[{block.velocity.x}, {block.velocity.y}]")

    running = True
    while running:
        curr_time = round(time(), 2)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        if (not is_cycle and len(measurements) > 10) or (is_cycle and len(collisions) > model_cycles_amount):
            running = False

        if abs(block.velocity[0]) < settings.precision and abs(block.velocity[1]) < settings.precision:
            measurements.append(Measurement(curr_time, block.position, block.velocity))
            print(measurements[-1].to_str_stop())

        display.fill((65, 65, 65))
        space.debug_draw(draw_options)
        pygame.display.update()
        clock.tick(settings.fps)
        space.step(1 / settings.fps)
    pygame.quit()

    print("--SIMULATION END--")
    end_time = round(time(), 2)
    end_measurement = Measurement(end_time, block.position, block.velocity)
    print(f"end time={end_time} "
          f"end_measurement={end_measurement} "
          f"detected wall-block collisions={len(collisions)} "
          f"detected stops={len(measurements)} "
          f"duration={end_time - start_time}")

    collisions.insert(0, start_measurement)
    collisions.append(end_measurement)

    return collisions, measurements, (end_time - start_time)


def collect_cycles(measurements: list[Measurement], collisions: list[Measurement]) -> list[Cycle]:
    cycles = []
    measurement_ndx = 0
    for i in range(0, len(collisions) - 1):
        measurement = Measurement(-1, Vec2d(1E50, 1E50),
                                  Vec2d(1E50, 1E50))
        start = collisions[i]
        end = collisions[i + 1]
        while measurement_ndx < len(measurements) and measurements[measurement_ndx].time < end.time:
            if measurements[measurement_ndx].velocity.value < measurement.velocity.value:
                measurement = measurements[measurement_ndx]
            measurement_ndx += 1
        if measurement.time != -1:
            cycles.append(Cycle(i, start, measurement, end))
    return cycles


def retrieve_results(measurements: list[Measurement], collisions: list[Measurement], scale: int, is_full: bool) \
        -> list[ResultMeasured]:
    results = []
    cycles = collect_cycles(measurements, collisions)
    for cycle in cycles:
        results.append(ResultMeasured(cycle, scale, is_full))
    return results


def calculate_theoretical_model(inp: Input, settings: Settings) -> list[ResultModel]:
    g = abs(settings.gravity.y / settings.scale)
    if (inp.friction * cos(inp.tilt)) / (sin(inp.tilt)) >= 1:
        return [ResultModel(0, inp.velocity_u, inp.tilt, inp.friction, g, False)]
    results = [ResultModel(0, inp.velocity_u, inp.tilt, inp.friction, g, True)]
    i = 1
    while results[-1].end_velocity.value > settings.precision / settings.scale:
        results.append(
            ResultModel(i, Vector(-results[-1].end_velocity.x, -results[-1].end_velocity.y, UNIT_VELOCITY), inp.tilt,
                        inp.friction, g, True))
        i += 1
    return results


def result_vector_str(measure: Vector, model: Vector, error: Vector, error_r: tuple[float, float], error_r_v: float):
    return f"{measure} = {measure.str_value()} || {model} = {model.str_value()}\n" \
           f"error = {error} ({error_r[0] * 100}%, {error_r[1] * 100}%) = {error.str_value()} ({error_r_v * 100}%)\n"


def result_scalar_str(measure: str, model: str, error: str, error_r: float):
    return f"{measure} || {model}\n" \
           f"Error = {error} ({error_r * 100}%)\n"


def result_str(measure: ResultMeasured, model: ResultModel, error: Error):
    s = f"***CYCLE NUMBER {model.number}***\n"
    if not model.is_full:
        s += "(This cycle is NOT FULL. Block has stopped in the middle of the cycle.)\n"
    s += "DURATION\nFrom start to middle = " + result_scalar_str(time_str(measure.duration1),
                                                                 time_str(model.duration1),
                                                                 time_str(error.duration1),
                                                                 error.duration1_rel)
    s += "From middle to end = " + result_scalar_str(time_str(measure.duration2 if model.is_full else "NaN "),
                                                     time_str(model.duration2 if model.is_full else "NaN "),
                                                     time_str(error.duration2),
                                                     error.duration2_rel)
    s += "Full = " + result_scalar_str(
        time_str(measure.duration1 + measure.duration2 if model.is_full else measure.duration1),
        time_str(model.duration1 + model.duration2 if model.is_full else model.duration1),
        time_str(error.duration),
        error.duration_rel
    )
    s += f"START VELOCITY\n" + result_vector_str(measure.start_velocity, model.start_velocity, error.start_velocity,
                                                 error.start_velocity_rel, error.start_velocity_value_rel)
    s += f"END VELOCITY\n" + result_vector_str(measure.end_velocity, model.end_velocity, error.end_velocity,
                                               error.end_velocity_rel, error.end_velocity_value_rel)
    s += f"REACH\n" + result_vector_str(measure.reach, model.reach, error.reach, error.reach_rel, error.reach_value_rel)
    return s


def read_input(mass: float, scale: int) -> Input:
    angle = float(input("Tilt of plane (rad) (0; pi/2) = "))
    friction = float(input("Friction coefficient (Coulomb friction) = "))
    velocity = float(input("Starting velocity (m/s) (parallel to slope) = "))
    inp = Input(angle, mass, velocity, friction, scale)
    print(inp.to_str_usr())
    print(inp)
    return inp


def gen_ascii():
    return fr"""
 _____           _ _                _  ______ _                   ______          _           _   
|_   _|         | (_)              | | | ___ \ |                  | ___ \        (_)         | |  
  | | _ __   ___| |_ _ __   ___  __| | | |_/ / | __ _ _ __   ___  | |_/ / __ ___  _  ___  ___| |_ 
  | || '_ \ / __| | | '_ \ / _ \/ _` | |  __/| |/ _` | '_ \ / _ \ |  __/ '__/ _ \| |/ _ \/ __| __|
 _| || | | | (__| | | | | |  __/ (_| | | |   | | (_| | | | |  __/ | |  | | | (_) | |  __/ (__| |_ 
 \___/_| |_|\___|_|_|_| |_|\___|\__,_| \_|   |_|\__,_|_| |_|\___| \_|  |_|  \___/| |\___|\___|\__|
                                                                                _/ |              
                                                                               |__/                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 
InclinedPlaneProject v{VERSION}
    """


def main():
    print(gen_ascii())

    settings = Settings(10, Vector(0, -9.81, UNIT_ACCELERATION), RESOLUTION, 40, 0.1, 50)
    print(settings)
    inp = read_input(1, settings.scale)

    models = calculate_theoretical_model(inp, settings)
    is_full = models[0].is_full

    space, block = init_space(inp, settings)
    collisions, measurements, sim_duration = simulate(space, block, inp, settings, len(models), is_full)
    results = retrieve_results(measurements, collisions, settings.scale, is_full)

    print(
        f"---RESULTS---\n"
        f"{inp.pretty_str()}"
        f"Gravity vector = {settings.gravity * (1 / settings.scale)}\n"
        f"*Mass does not affect results.\n"
        f"Results:\n"
        f"CYCLE - One cycle is counted from block bouncing off the wall to block falling back on the wall.\n"
        f"Each cycle result contains measured results compared to the theory model.\n"
        f"Result pattern: 'measured' || 'model' error = 'error' ('rel. error')\n"
        f"Cycles = {len(models)}\n"
        f"Full duration = {time_str(sim_duration)}\n"
    )
    for i in range(0, len(models)):
        print(result_str(results[i], models[i], Error(results[i], models[i])))


main()
