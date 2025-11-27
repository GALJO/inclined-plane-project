import sys
from math import sin, cos, tan, radians, sqrt
from time import sleep, time

import pygame
import pymunk.pygame_util
from pymunk import Arbiter, Space, Vec2d, Body

VERSION = "1.0 BETA"
RESOLUTION = (800, 800)


def translate_abs(x: float, y: float):
    return x, RESOLUTION[1] - y


def translate(x: float, y: float):
    return x, -y


class Vector:

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def translated(self) -> tuple[float, float]:
        return translate(self.x, self.y)

    def translated_abs(self) -> tuple[float, float]:
        return translate_abs(self.x, self.y)

    def value(self) -> float:
        return sqrt(self.x ** 2 + self.y ** 2)

    def __str__(self):
        return f"[{self.x}, {self.y}]"

    def to_str_translated(self) -> str:
        x, y = translate(self.x, self.y)
        return f"[{x}, {y}]"

    def to_str_abs(self) -> str:
        x, y = translate_abs(self.x, self.y)
        return f"[{x}, {y}]"


class Input:
    def __init__(self, _tilt: int, _mass: int, _velocity: float, _friction: float, _scale: int):
        self.tilt_u = _tilt
        self.mass_u = _mass
        self.velocity_u = Vector(_velocity * cos(radians(_tilt)), _velocity * sin(radians(_tilt)))
        self.tilt = radians(_tilt)
        self.mass = _mass * _scale
        self.velocity = Vector(self.velocity_u.x * _scale, self.velocity_u.y * _scale)
        self.friction = _friction

    def to_str_usr(self) -> str:
        return (f"User Input: "
                f"tilt={self.tilt_u} "
                f"mass={self.mass_u} "
                f"velocity={self.velocity_u} "
                f"friction={self.friction}")

    def __str__(self):
        return (f"Input: "
                f"tilt={self.tilt} "
                f"mass={self.mass} "
                f"velocity={self.velocity} "
                f"friction={self.friction}")


class Settings:
    def __init__(self, _scale: int, _gravity: Vector, _resolution: tuple[int, int], _block_size: int, _fps: int):
        self.scale = _scale
        self.gravity = _gravity
        self.resolution = _resolution
        self.block_size = _block_size
        self.fps = _fps

    def __str__(self):
        return (
            f"Settings: scale={self.scale} gravity={self.gravity.to_str_translated()} "
            f"resolution=({self.resolution[0]}, {self.resolution[1]}) fps={self.fps}")


class Measurement:
    def __init__(self, _time: float, _position: Vec2d, _velocity: Vec2d):
        self.time = _time
        x, y = translate_abs(_position.x, _position.y)
        self.position = Vector(x, y)
        x, y = translate(_velocity.x, _velocity.y)
        self.velocity = Vector(x, y)

    def to_str_stop(self) -> str:
        return (f"[{self.time}] Block stop detection. "
                f"pos={self.position.to_str_abs()} vel={self.velocity.to_str_translated()}")

    def to_str_col(self) -> str:
        return (f"[{self.time}] Block-wall collision. "
                f"pos={self.position.to_str_abs()} "
                f"vel={self.velocity.to_str_translated()}")


class Cycle:
    def __init__(self, _number: int, _start_collision: Measurement, _middle_measurement: Measurement,
                 _end_collision: Measurement):
        self.number = _number
        self.start = _start_collision
        self.middle = _middle_measurement
        self.end = _end_collision


class Result:
    def __init__(self, cycle: Cycle, scale: int):
        self.number = cycle.number
        self.duration = cycle.end.time - cycle.start.time
        self.start_velocity = Vector(abs(cycle.start.velocity.x) / scale, -abs(cycle.start.velocity.y) / scale)
        self.end_velocity = Vector(-abs(cycle.end.velocity.x) / scale, abs(cycle.end.velocity.y) / scale)
        ## start -> middle distance
        self.distance = Vector(abs(cycle.start.position.x - cycle.middle.position.x) / scale,
                               -abs(cycle.start.position.y - cycle.middle.position.y) / scale)

    def pretty_str(self) -> str:
        return f"RESULTS FOR CYCLE NR {self.number}\n" \
               f"Duration of the cycle: {self.duration} s\n" \
               f"Starting with velocity: {self.start_velocity.to_str_translated()} m/s = {self.start_velocity.value()} m/s\n" \
               f"Ending with velocity: {self.end_velocity.to_str_translated()} m/s = {self.end_velocity.value()} m/s\n" \
               f"(velocity loss : {self.start_velocity.value() - self.end_velocity.value()} m/s)\n" \
               f"Distance traveled from start to middle (reach) : {self.distance.to_str_translated()} m = {self.distance.value()} m\n"


def init_space(inp: Input, settings: Settings) -> tuple[Space, Body]:
    print("Initializing space.")
    _space = pymunk.Space()
    _space.gravity = settings.gravity.translated()

    slope = pymunk.Segment(_space.static_body, translate_abs(50, 0),
                           translate_abs(5000, tan(inp.tilt) * 5000), 4)
    slope.friction = 1

    wall = pymunk.Segment(_space.static_body, translate_abs(100, 0),
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

    _space.add(block_body, block, slope, wall)
    print("Initialized space.")
    return _space, block_body


def handle_block_wall_collision(arbiter: Arbiter, space: Space, data: list[Measurement]) -> None:
    data.append(Measurement(round(time(), 2), arbiter.shapes[1].body.position, arbiter.shapes[1].body.velocity))
    print(data[-1].to_str_col())


def simulate(space: Space, block: Body, inp: Input, settings: Settings) -> tuple[list[Measurement], list[Measurement]]:
    display = pygame.display.set_mode(settings.resolution)
    draw_options = pymunk.pygame_util.DrawOptions(display)
    clock = pygame.time.Clock()

    vx, vy = inp.velocity.translated()
    block.apply_impulse_at_world_point((vx * inp.mass, vy * inp.mass), translate_abs(0, 0))

    pygame.init()
    print("--SIMULATION START--")
    print(f"start_time={round(time(), 2)} "
          f"start_pos=[{block.position.x}, {block.position.y}] "
          f"start_velocity=[{block.velocity.x}, {block.velocity.y}]")

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

    running = True
    while running:
        curr_time = round(time(), 2)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        if (len(collisions) >= 2
                and abs(collisions[-1].velocity.x - collisions[-2].velocity.x) <= settings.scale / 100
                and abs(collisions[-1].velocity.y - collisions[-2].velocity.x) <= settings.scale / 100):
            running = False

        if abs(block.velocity[0]) < 1 and abs(block.velocity[1]) < 1:
            measurements.append(Measurement(curr_time, block.position, block.velocity))
            print(measurements[-1].to_str_stop())

        display.fill((65, 65, 65))
        space.debug_draw(draw_options)
        pygame.display.update()
        clock.tick(settings.fps)
        space.step(1 / settings.fps)
    print("--SIMULATION END--")
    print(f"end time={round(time(), 2)}")
    print(f"detected wall-block collisions={len(collisions)}")
    print(f"detected stops={len(measurements)}")
    return collisions, measurements


def collect_cycles(measurements: list[Measurement], collisions: list[Measurement]) -> list[Cycle]:
    cycles = []
    measurement_ndx = 0
    for i in range(0, len(collisions) - 1):
        measurement = Measurement(-1, Vec2d(1E50, 1E50),
                                  Vec2d(1E50, 1E50))
        start = collisions[i]
        end = collisions[i + 1]
        while measurement_ndx < len(measurements) and measurements[measurement_ndx].time < end.time:
            if measurements[measurement_ndx].velocity.value() < measurement.velocity.value():
                measurement = measurements[measurement_ndx]
            measurement_ndx += 1
        if measurement.time != -1:
            cycles.append(Cycle(i + 1, start, measurement, end))
    return cycles


def retrieve_results(measurements: list[Measurement], collisions: list[Measurement], scale: int) -> list[Result]:
    results = []
    cycles = collect_cycles(measurements, collisions)
    for cycle in cycles:
        results.append(Result(cycle, scale))
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
    settings = Settings(10, Vector(0, -98.1), RESOLUTION, 40, 50)
    inp = Input(80, 1, 20, 0.5, settings.scale)
    print(inp.to_str_usr())
    print(inp)
    print(settings)

    space, block = init_space(inp, settings)
    collisions, measurements = simulate(space, block, inp, settings)
    results = retrieve_results(measurements, collisions, settings.scale)

    gx, gy = settings.gravity.translated()
    print(
        f"---RESULTS---\n"
        f"Input data:\n"
        f"Slope angle = {inp.tilt_u} degrees (= {inp.tilt} rad)\n"
        f"Start velocity vector (parallel to slope) = {inp.velocity_u.value()} m/s (= {inp.velocity_u.to_str_translated()} m/s)\n"
        f"Mass of the block = {inp.mass} kg\n"
        f"Dynamic friction coefficient between block and slope (Coulomb friction model) = {inp.friction}\n"
        f"Gravity vector = [{gx / settings.scale} {gy / settings.scale}] m/s^2\n"
        f"Technical notes:\n"
        f"- Block is treated as a point mass (inf inertia), with its center in the corner of the block.\n"
        f"- Simulation takes a few measurements when the block approaches to 0 velocity\n"
        f"and chooses the measure with smallest velocity recorded. It is not possible to record exactly 0 velocity.\n"
        f"- Mass does not affect results (and this is right).\n"
        f"CYCLE - One cycle begins when block starts moving up the slope and ends when block is back in its starting position.\n"
        f"Actual results:\n"
        f"Cycles recorded = {len(results)}\n"
    )
    for result in results:
        print(result.pretty_str())

    pygame.quit()


main()
