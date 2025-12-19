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
from pathlib import Path
from time import time

import pygame
import pymunk.pygame_util
from pymunk import Arbiter, Space, Vec2d, Body

from application.input.exceptions import InputParsingError
from application.input.model.Input import Input
from application.math_objects.Vector import *
from application.result.Error import Error
from application.result.Result import Measurement, Cycle, Result
from infrastructure.AppPorts import AppPorts
from infrastructure.config.Config import CONFIG
from infrastructure.log.utils.pre_logging import init_pre_logging
from infrastructure.print_banner import print_banner

VERSION = "1.0 BETA"
CONFIG_PATH = Path("./config.yaml")


def init_space(inp: Input) -> tuple[Space, Body]:
    """
    Function initializes Pymunk Space object for simulation.
    :param inp: Input data.
    :returns: Set up Space object and Body object of block.
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
    """
    Handler of block-wall collision. Saves the Measurement object and logs the collision.
    :param arbiter: Pymunk Arbiter - collision data object.
    :param space: Pymunk Space object.
    :param data: List of Measurements (one of results of simulation).
    """
    data.append(Measurement(round(time(), 2), arbiter.shapes[1].body.position, arbiter.shapes[1].body.velocity))
    logging.debug(f"Block-wall collision detected: measurement={data[-1]}")


def simulate(space: Space, block: Body, inp: Input, model_cycles_amount: int, is_full: bool) -> \
        tuple[list[Measurement], list[Measurement], Scalar]:
    """
    Simulates the scenario for given data using Pymunk physics engine.
    :param space: Pymunk Space object.
    :param block: Pymunk Body object of block.
    :param inp: Input data.
    :param model_cycles_amount: Expected amount of cycles based on model results.
    :param is_full: True if cycle is full in model results.
    Cycle is not full only if 3rd point of cycle did not happen (block stopped in 2nd point).
    :return: Two lists of Measurement objects - first one with detected wall-block collision events,
    second one with detected block stop events - and duration of simulation.
    Second list also contains measures taken at start and end of the simulation.
    """
    display = pygame.display.set_mode(CONFIG.resolution)
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


def collect_cycles(stop_events: list[Measurement], collision_events: list[Measurement]) -> list[Cycle]:
    """
    Parses measurements from simulation and converts them to list of Cycle objects.
    :param stop_events: Measurements of block stop events from simulation.
    :param collision_events: Measurements of block-wall collision events from simulation.
    :return: List of Cycle objects based on simulation events.
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
            cycles.append(Cycle(cycle_i, start, event, end))
            logging.debug(f"Collected cycle: cycle={cycles[-1]}")
            cycle_i += 1
    logging.info(f"Collected cycles: n={len(cycles)}")
    return cycles


def prepare_results(stop_events: list[Measurement], collision_events: list[Measurement], is_full: bool) \
        -> list[Result]:
    """
    Parses measurements from simulation, divides them to cycles and prepares results.
    :param stop_events: Measurements of block stop events from simulation.
    :param collision_events: Measurements of block-wall collision events from simulation.
    :param is_full: True if cycle is full.
    Cycle is not full only if 3rd point of cycle did not happen (block stopped in 2nd point).
    :return: List with Result object for each cycle.
    """
    logging.info(f"Preparing simulation results: is_full={is_full}")
    results = []
    cycles = collect_cycles(stop_events, collision_events)
    for cycle in cycles:
        results.append(Result.measured(cycle, is_full))
        logging.debug(f"Prepared result: result={results[-1]} cycle={cycle}")
    logging.info(f"Prepared simulation results: n={len(results)}")
    return results


def prepare_errors(measured: list[Result], model: list[Result]) -> list[Error]:
    logging.debug(f"Preparing errors.")
    errors = []
    for i in range(0, len(model)):
        errors.append(Error(measured[i], model[i]))
        logging.debug(f"Prepared error: error={errors[-1]} measured={measured[i]} model={model[i]}")
    logging.info(f"Prepared errors: n={len(errors)}")
    return errors


def calculate_theoretical_model(user_input: Input) -> list[Result]:
    """
    Prepares model results based on physics formulas.
    :param user_input: Input data.
    :return: List with Result object for each cycle.
    """
    logging.info(f"Calculating model: input={user_input}")
    results = [Result.model(0,
                            user_input.velocity,
                            user_input.tilt.value,
                            user_input.friction.value,
                            CONFIG.g,
                            False)]
    if (user_input.friction * cos(user_input.tilt.value)) / (sin(user_input.tilt.value)) >= 1:
        logging.info(f"Not full cycle occurred. result={results[0]}")
        logging.info(f"Calculated model: n={len(results)}")

    results = [Result.model(0,
                            user_input.velocity,
                            user_input.tilt.value,
                            user_input.friction.value,
                            CONFIG.g,
                            True)]
    logging.debug(f"Calculated model result: n={0} result={results[-1]}")
    i = 1
    while results[-1].end_velocity.value > CONFIG.measure_precision:
        results.append(Result.model(i,
                                    results[-1].end_velocity,
                                    user_input.tilt.value,
                                    user_input.friction.value,
                                    CONFIG.g,
                                    True))
        logging.debug(f"Calculated model result: n={i} result={results[-1]}")
        i += 1

    logging.info(f"Calculated model: n={len(results)}")
    return results


def handle_error(e: InputParsingError) -> None:
    print(f"Wrong {e.field.name} field given: {e.desc} ({e.code}). Try again.")


def read_console() -> Input:
    """
    Reads user's input from console.
    :returns: User Input.
    """
    i = 0
    while True:
        logging.info(f"Reading input: trial nr {i}")
        angle = input("Tilt of plane (rad) (0, 0.5pi) = ")
        logging.debug(f"Received input: angle={angle}")
        friction = input("Friction coefficient (Coulomb friction) (0, inf) = ")
        logging.debug(f"Received input: friction={friction}")
        mass = input("Block's mass (kg) (0, inf) = ")
        logging.debug(f"Received input: mass={mass}")
        velocity = input("Starting velocity (m/s) (parallel to slope) (0, inf) = ")
        logging.debug(f"Received input: velocity={velocity}")
        try:
            inp = Input.user(angle, mass, velocity, friction)
            logging.info(f"Successfully read input after {i + 1} trial(s): input={inp}")
            return inp
        except InputParsingError as e:
            logging.error(f"Error while reading user's input - retrying to get input: e={e}")
            handle_error(e)
            i += 1


def main():
    init_pre_logging()
    CONFIG.update(CONFIG_PATH)

    ports = AppPorts()
    ports.log_port.setup()

    print_banner(VERSION)

    user_input = read_console()
    simulation_input = Input.simulation(user_input)

    model = calculate_theoretical_model(user_input)
    is_full = model[0].is_full

    space, block = init_space(simulation_input)
    collisions, measurements, sim_duration = simulate(space, block, simulation_input, len(model), is_full)
    measured = prepare_results(measurements, collisions, is_full)
    errors = prepare_errors(measured, model)

    ports.output_port.send_output(measured, model, errors)


main()
