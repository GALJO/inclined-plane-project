import sys
from math import sin, cos, tan, radians, sqrt, degrees
from time import time

import pygame
import pymunk.pygame_util
from pymunk import Arbiter, Space, Vec2d, Body

VERSION = "1.0 BETA"
RESOLUTION = (800, 800)

D = 1e-6

UNIT_VELOCITY = "m/s"
UNIT_ACCELERATION = "m/s^2"
UNIT_MASS = "kg"
UNIT_DISTANCE = "m"
UNIT_TIME = "s"


def translate_abs(x: float, y: float):
    return x, RESOLUTION[1] - y


def translate(x: float, y: float):
    return x, -y


def str_time(t: float):
    if t < D:
        return "dt"
    return t


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


class Input:
    def __init__(self, _tilt: float, _mass: int, _velocity: float, _friction: float, _scale: int):
        self.tilt = _tilt
        self.mass_u = _mass
        self.velocity_u = Vector(_velocity * cos(_tilt), _velocity * sin(_tilt), UNIT_VELOCITY)
        self.mass = _mass * _scale
        self.velocity = Vector(self.velocity_u.x * _scale, self.velocity_u.y * _scale, UNIT_VELOCITY)
        self.friction = _friction

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
        self.gravity = Vector(_gravity.x * _scale, _gravity.y * _scale, UNIT_ACCELERATION)
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
        self.time = _time
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


class Result:
    def __init__(self, cycle: Cycle, scale: int, is_full: bool):
        self.number = cycle.number
        self.is_full = is_full
        self.duration1 = cycle.middle.time - cycle.start.time

        if not is_full:
            self.duration2 = float("inf")
        else:
            self.duration2 = cycle.end.time - cycle.middle.time
        self.start_velocity = Vector(cycle.start.velocity.x / scale, cycle.start.velocity.y / scale, UNIT_VELOCITY)
        self.end_velocity = Vector(cycle.end.velocity.x / scale, cycle.end.velocity.y / scale, UNIT_VELOCITY)
        ## start -> middle distance
        self.reach = Vector(abs(cycle.start.position.x - cycle.middle.position.x) / scale,
                            abs(cycle.start.position.y - cycle.middle.position.y) / scale, UNIT_DISTANCE)

    def pretty_str(self) -> str:
        _str = f"RESULTS FOR CYCLE NR {self.number}\n"

        if not self.is_full:
            _str += f"(NOT FULL CYCLE)\n"
        _str += f"Duration from start to middle: {self.duration1} {UNIT_TIME}\n" \
                f"Duration from middle to end: {self.duration2} {UNIT_TIME}\n"
        if self.is_full:
            _str += f"(Full duration {self.duration1 + self.duration2} {UNIT_TIME})\n"

        return _str + f"Starting with velocity: {self.start_velocity} = {self.start_velocity.str_value()}\n" \
                      f"Ending with velocity: {self.end_velocity} = {self.end_velocity.str_value()}\n" \
                      f"(velocity loss : {self.start_velocity.value - self.end_velocity.value}{UNIT_VELOCITY}\n" \
                      f"Distance traveled from start to middle (reach) : {self.reach} = {self.reach.str_value()} \n"


class ResultModel:
    def __init__(self, _cycle_n: int, _start_velocity: Vector, _tilt: float, _fr: float, _g: float, _is_full: bool):
        v1 = _start_velocity.value
        reach_value = v1 ** 2 / (2 * _g * (_fr * cos(_tilt) + sin(_tilt)))
        end_velocity_value = (2 * tan(_tilt) - _fr) / (2 * (_fr + tan(_tilt)))

        self.number = _cycle_n
        self.is_full = _is_full
        self.duration1 = v1 / (_g * (sin(_tilt) + _fr * cos(_tilt)))

        if not _is_full:
            self.duration2 = -1
        else:
            self.duration2 = end_velocity_value / (_g * (sin(_tilt) - _fr * cos(_tilt)))

        self.start_velocity = _start_velocity

        if not _is_full:
            self.end_velocity = Vector(0, 0, UNIT_VELOCITY)
        else:
            end_velocity_value = v1 * sqrt(end_velocity_value)
            self.end_velocity = Vector(-cos(_tilt) * end_velocity_value, sin(_tilt) * end_velocity_value, UNIT_VELOCITY)

        self.reach = Vector(cos(_tilt) * reach_value, -sin(_tilt) * reach_value, UNIT_DISTANCE)


def init_space(inp: Input, settings: Settings) -> tuple[Space, Body]:
    print("Initializing space.")
    space = pymunk.Space()
    space.gravity = settings.gravity.translated()

    slope = pymunk.Segment(space.static_body, translate_abs(50, 0),
                           translate_abs(5000, tan(inp.tilt) * 5000), 4)
    slope.friction = 1

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

    space.add(block_body, block, slope, wall)
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

    block.apply_impulse_at_world_point((inp.velocity.x * inp.mass, inp.velocity.y * inp.mass), translate_abs(0, 0))

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


def retrieve_results(measurements: list[Measurement], collisions: list[Measurement], scale: int, is_full: bool) -> list[
    Result]:
    results = []
    cycles = collect_cycles(measurements, collisions)
    for cycle in cycles:
        results.append(Result(cycle, scale, is_full))
    return results


def calculate_theoretical_model(inp: Input, settings: Settings) -> list[ResultModel]:
    g = abs(settings.gravity.y)
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
    inp = Input(radians(80), 5, 20, 0.5, settings.scale)
    print(inp.to_str_usr())
    print(inp)
    print(settings)

    models = calculate_theoretical_model(inp, settings)
    is_full = models[0].is_full

    space, block = init_space(inp, settings)
    collisions, measurements, sim_duration = simulate(space, block, inp, settings, len(models), is_full)
    results = retrieve_results(measurements, collisions, settings.scale, is_full)

    print(
        f"---RESULTS---\n"
        f"Input data:\n"
        f"Slope angle = {inp.tilt} rad (= {degrees(inp.tilt)} degrees)\n"
        f"Start velocity vector (parallel to slope) = {inp.velocity_u} ({inp.velocity_u.str_value()})\n"
        f"Mass of the block* = {inp.mass_u}{UNIT_MASS}\n"
        f"Dynamic friction coefficient between block and slope (Coulomb friction model) = {inp.friction}\n"
        f"Gravity vector = {settings.gravity}\n"
        f"*Mass do not affect results."
        f"Results:\n"
        f"CYCLE - One cycle is counted from block bouncing off the wall to block falling back on the wall.\n"
        f"Cycles recorded = {len(results)}\n"
        f"Full duration = {sim_duration}{UNIT_TIME}\n"
    )
    if not is_full:
        print("**Recorded cycle is not full. It means that the block has stopped in the middle of the plane.**")
    for result in results:
        print(result.pretty_str())


main()
