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
import sys
from math import sin, cos, tan, radians
from time import time

import pygame
import pymunk.pygame_util
from pymunk import Arbiter, Space, Vec2d, Body

from application.input.model.input import Input
from application.math.vector import *
from application.result.error import Error
from application.result.result import Measurement, Cycle, Result
from infrastructure.app_ports import AppPorts
from infrastructure.catcher import catcher
from infrastructure.config.config import CONFIG
from infrastructure.config.init_config import INIT_CONFIG
from infrastructure.log.util.pre_logging import init_pre_logging
from infrastructure.print_banner import print_banner


def init_space(inp: Input) -> tuple[Space, Body]:
    """Function initializes the simulation's space.

    :param inp: Input: The user's input.
    :returns: Pymunk space and the point's body.
    :rtype: tuple[Space, Body]

    """
    logging.info(f"Initializing simulation space: input={inp}")
    space = pymunk.Space()
    space.gravity = (0, CONFIG.g * CONFIG.scale)

    plane = pymunk.Segment(space.static_body, translate_abs(50, 0),
                           translate_abs(10000, tan(inp.tilt.value) * 10000), 4)
    plane.friction = 1

    logging.debug(f"Initialized object PLANE: body={plane.body} "
                  f"a={plane.a} "
                  f"b={plane.b} "
                  f"radius={plane.radius} "
                  f"friction={plane.friction}")

    wall = pymunk.Segment(space.static_body, translate_abs(100, 0),
                          translate_abs(0, (100 / tan(inp.tilt.value))), 4)
    wall.elasticity = 1
    wall.collision_type = 1
    logging.debug(f"Initialized object WALL: body={wall.body} "
                  f"a={wall.a} "
                  f"b={wall.b} "
                  f"radius={wall.radius} "
                  f"elasticity={wall.elasticity} "
                  f"collision_type={wall.collision_type}")

    block_body = pymunk.Body(mass=inp.mass.value,
                             moment=pymunk.moment_for_box(sys.float_info.max,
                                                          (CONFIG.block_size, CONFIG.block_size)))
    block_body.angle = radians(270) - inp.tilt.value
    block_body.position = translate_abs(100 - 50 * sin(inp.tilt.value) ** 2,
                                        50 * sin(inp.tilt.value) * cos(inp.tilt.value))

    block = pymunk.Poly(block_body, [(0, 0), (0, CONFIG.block_size),
                                     (CONFIG.block_size, 0), (CONFIG.block_size, CONFIG.block_size)])
    block.elasticity = 1
    block.friction = inp.friction.value
    block.collision_type = 1
    logging.debug(f"Initialized object BLOCK: body={block.body} "
                  f"angle={block.body.angle} "
                  f"position={block.body.position} "
                  f"gravity_center={block.center_of_gravity} "
                  f"elasticity={block.elasticity} "
                  f"friction={block.friction} "
                  f"collision_type={block.collision_type}")

    space.add(block_body, block, plane, wall)
    logging.info(f"Initialized simulation space with parameters: gravity={space.gravity} "
                 f"bodies={space.bodies}")
    return space, block_body


def handle_collision(arbiter: Arbiter, space: Space, data: list[Measurement]) -> None:
    """Handles the collision event.

    :param arbiter: Arbiter: Collision data object.
    :param space: Space: Pymunk space.
    :param data: list[Measurement]: List to append Measurement from collision.

    """
    data.append(Measurement(round(time(), 2), arbiter.shapes[1].body.position, arbiter.shapes[1].body.velocity))
    logging.debug(f"Block-wall collision detected: measurement={data[-1]}")


def simulate(space: Space, block: Body, inp: Input, model_cycles_amount: int, is_full: bool) -> \
        tuple[list[Measurement], list[Measurement], Scalar]:
    """Simulates the scenario for given data in physics engine.

    Simulation cycle: Look up the Cycle object docstring.

    Simulation events: Look up the Measurement object docstring.

    :param space: Space: The simulation's space.
    :param block: Body: The point's body.
    :param inp: Input: The user's input.
    :param model_cycles_amount: int: Expected amount of cycles based on model results.
    :param is_full: bool: Is cycle full in model results?
    :returns: A list of Measurements from the collision events, a list of Measurements from the stop events, elapsed duration of the simulation.
    :rtype: tuple[list[Measurement], list[Measurement], Scalar]
    """
    display = pygame.display.set_mode(CONFIG.resolution)
    pygame.display.set_caption("InclinedPlane -- SIMULATION")
    draw_options = pymunk.pygame_util.DrawOptions(display)
    clock = pygame.time.Clock()
    logging.debug(f"Set up pygame display: resolution={CONFIG.resolution} fps={CONFIG.fps}")

    vel = inp.velocity.translated()
    block.apply_impulse_at_world_point((vel.x.value * inp.mass.value, vel.y.value * inp.mass.value),
                                       translate_abs(0, 0))

    collision_events: list[Measurement] = []
    stop_events: list[Measurement] = []
    space.on_collision(
        1,
        1,
        handle_collision,
        None,
        None,
        None,
        data=collision_events
    )

    pygame.init()

    start_time = Scalar(round(time(), 2), CONFIG.unit.time)
    start_measurement = Measurement(start_time.value, block.position, block.velocity)
    logging.info("Running simulation: "
                 f"start_time={start_time} "
                 f"start_measurement={start_measurement} "
                 f"start_pos={block.position} "
                 f"start_velocity={block.velocity}")
    running = True
    while running:
        curr_time = round(time(), 2)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        if (not is_full and len(stop_events) > 10) or (is_full and len(collision_events) > model_cycles_amount):
            running = False

        if abs(block.velocity[0]) < (CONFIG.measure_precision * CONFIG.scale) and abs(block.velocity[1]) < (
                CONFIG.measure_precision * CONFIG.scale):
            stop_events.append(Measurement(curr_time, block.position, block.velocity))
            logging.debug(f"Block stop detected: measurement={stop_events[-1]}")

        display.fill((65, 65, 65))
        space.debug_draw(draw_options)
        pygame.display.update()
        clock.tick(CONFIG.fps)
        space.step(1 / CONFIG.fps)
    pygame.quit()

    end_time = Scalar(round(time(), 2), CONFIG.unit.time)
    end_measurement = Measurement(end_time.value, block.position, block.velocity)
    logging.info(f"Simulation finished: "
                 f"duration={end_time - start_time} "
                 f"end_time={end_time} "
                 f"end_measurement={end_measurement} "
                 f"wall-block collisions n={len(collision_events)} "
                 f"block stops n={len(stop_events)}")

    collision_events.insert(0, start_measurement)
    collision_events.append(end_measurement)

    return collision_events, stop_events, end_time - start_time


def collect_cycles(stop_events: list[Measurement], collision_events: list[Measurement], is_full: bool) -> list[Cycle]:
    """Parses simulation's results to simulation's Cycles.

    :param stop_events: list[Measurement]: Stop events measurements.
    :param collision_events: list[Measurement]: Collision events measurements.
    :param is_full: bool: Is cycle full?
    :returns: Simulation's cycles.
    :rtype: list[Cycle]

    """
    logging.debug(f"Collecting cycles.")
    cycles = []
    measurement_ndx = 0
    cycle_i = 0
    for i in range(0, len(collision_events) - 1):
        event = Measurement(-1, Vec2d(1E50, 1E50),
                            Vec2d(1E50, 1E50))
        start = collision_events[i]
        end = collision_events[i + 1]
        while measurement_ndx < len(stop_events) and stop_events[measurement_ndx].time < end.time:
            if stop_events[measurement_ndx].velocity.value < event.velocity.value:
                event = stop_events[measurement_ndx]
            measurement_ndx += 1
        if event.time != -1:
            cycles.append(Cycle(cycle_i, start, event, end, is_full))
            logging.debug(f"Collected cycle: cycle={cycles[-1]}")
            cycle_i += 1
    logging.info(f"Collected cycles: n={len(cycles)}")
    return cycles


def prepare_results(stop_events: list[Measurement], collision_events: list[Measurement], is_full: bool) \
        -> list[Result]:
    """Parses simulation's measurements into readable results.

    :param stop_events: list[Measurement]: Stop events measurements.
    :param collision_events: list[Measurement]: Collision events measurements.
    :param is_full: bool: Is cycle full?
    :returns: List of results.
    :rtype: list[Result]

    """
    logging.info(f"Preparing simulation results: is_full={is_full}")
    results = []
    cycles = collect_cycles(stop_events, collision_events, is_full)
    for cycle in cycles:
        results.append(Result.measured(cycle))
        logging.debug(f"Prepared result: result={results[-1]} cycle={cycle}")
    logging.info(f"Prepared simulation results: n={len(results)}")
    return results


def prepare_errors(measured: list[Result], model: list[Result]) -> list[Error]:
    """Prepares Error objects based on results.

    :param measured: list[Result]: Simulated results.
    :param model: list[Result]: Model results.
    :returns: List of errors.
    :rtype: list[Error]
    """
    logging.debug(f"Preparing errors.")
    errors = []
    for i in range(0, len(model)):
        errors.append(Error(measured[i], model[i]))
        logging.debug(f"Prepared error: error={errors[-1]} measured={measured[i]} model={model[i]}")
    logging.info(f"Prepared errors: n={len(errors)}")
    return errors


def calculate_theoretical_model(inp: Input) -> list[Result]:
    """Prepares model results based on physics formulas.

    :param inp: Input: The user's input.
    :returns: Results.
    :rtype: list[Result]
    """
    logging.info(f"Calculating model: input={inp}")
    results = [Result.model(0,
                            inp.velocity,
                            inp.tilt.value,
                            inp.friction.value,
                            CONFIG.g,
                            False)]
    if (inp.friction * cos(inp.tilt.value)) / (sin(inp.tilt.value)) >= 1:
        logging.info(f"Not full cycle occurred. result={results[0]}")
        logging.info(f"Calculated model: n={len(results)}")

    results = [Result.model(0,
                            inp.velocity,
                            inp.tilt.value,
                            inp.friction.value,
                            CONFIG.g,
                            True)]
    logging.debug(f"Calculated model result: n={0} result={results[-1]}")
    i = 1
    while results[-1].end_velocity.value > CONFIG.measure_precision:
        results.append(Result.model(i,
                                    results[-1].end_velocity,
                                    inp.tilt.value,
                                    inp.friction.value,
                                    CONFIG.g,
                                    True))
        logging.debug(f"Calculated model result: n={i} result={results[-1]}")
        i += 1

    logging.info(f"Calculated model: n={len(results)}")
    return results


@catcher
def main():
    # Initialization
    init_pre_logging()
    CONFIG.update(INIT_CONFIG.config_path)
    ports = AppPorts()
    ports.log.setup()
    print_banner(INIT_CONFIG.version)

    # Reading input
    user_input = ports.input.get_input()
    simulation_input = Input.simulation(user_input)

    # Calculating model
    model = calculate_theoretical_model(user_input)
    is_full = model[0].is_full

    # Simulation
    space, block = init_space(simulation_input)
    collisions, measurements, sim_duration = simulate(space, block, simulation_input, len(model), is_full)

    # Preparing & sending results
    measured = prepare_results(measurements, collisions, is_full)
    errors = prepare_errors(measured, model)
    ports.output.send_output(measured, model, errors)


main()
