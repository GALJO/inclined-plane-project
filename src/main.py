import logging
import sys
from math import sin, cos, tan, radians
from time import time

import pygame
import pymunk.pygame_util
from pymunk import Arbiter, Space, Vec2d, Body

from application.input.Input import Input
from application.math_objects.Vector import *
from application.result.Error import Error
from application.result.Result import Measurement, Cycle, Result
from infrastructure.constants import *
from infrastructure.logging_init import logging_init
from infrastructure.ports_setup import AppPorts
from infrastructure.print_banner import print_banner


def init_space(inp: Input) -> tuple[Space, Body]:
    """
    Function initializes Pymunk Space object for simulation.
    :param inp: Input data.
    :returns: Set up Space object and Body object of block.
    :rtype: tuple[Space, Body]
    """
    space = pymunk.Space()
    space.gravity = SIM_GRAVITY

    plane = pymunk.Segment(space.static_body, translate_abs(50, 0),
                           translate_abs(5000, tan(inp.tilt.value) * 5000), 4)
    plane.friction = 1

    wall = pymunk.Segment(space.static_body, translate_abs(100, 0),
                          translate_abs(0, (100 / tan(inp.tilt.value))), 4)
    wall.elasticity = 1
    wall.collision_type = 1

    block_body = pymunk.Body(mass=inp.mass.value,
                             moment=pymunk.moment_for_box(sys.float_info.max,
                                                          (SIM_BLOCK_SIZE, SIM_BLOCK_SIZE)))
    block_body.angle = radians(270) - inp.tilt.value
    block_body.position = translate_abs(100 - 50 * sin(inp.tilt.value) ** 2,
                                        50 * sin(inp.tilt.value) * cos(inp.tilt.value))

    block = pymunk.Poly(block_body, [(0, 0), (0, SIM_BLOCK_SIZE),
                                     (SIM_BLOCK_SIZE, 0), (SIM_BLOCK_SIZE, SIM_BLOCK_SIZE)])
    block.elasticity = 1
    block.friction = inp.friction.value
    block.collision_type = 1

    space.add(block_body, block, plane, wall)
    return space, block_body


def handle_block_wall_collision(arbiter: Arbiter, space: Space, data: list[Measurement]) -> None:
    """
    Handler of block-wall collision. Saves the Measurement object and logs the collision.
    :param arbiter: Pymunk Arbiter - collision data object.
    :param space: Pymunk Space object.
    :param data: List of Measurements (one of results of simulation).
    """
    data.append(Measurement(round(time(), 2), arbiter.shapes[1].body.position, arbiter.shapes[1].body.velocity))
    logging.info(f"Block-wall collision detected, {data[-1]}")


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
    display = pygame.display.set_mode(RESOLUTION)
    draw_options = pymunk.pygame_util.DrawOptions(display)
    clock = pygame.time.Clock()
    logging.debug(f"Set up pygame display. resolution={RESOLUTION} fps={SIM_FPS}")

    vel = inp.velocity.translated()
    block.apply_impulse_at_world_point((vel.x.value * inp.mass.value, vel.y.value * inp.mass.value),
                                       translate_abs(0, 0))

    collision_events: list[Measurement] = []
    stop_events: list[Measurement] = []
    space.on_collision(
        1,
        1,
        handle_block_wall_collision,
        None,
        None,
        None,
        data=collision_events
    )

    pygame.init()

    logging.info("Running simulation.")
    start_time = Scalar(round(time(), 2), UNIT_TIME)
    start_measurement = Measurement(start_time.value, block.position, block.velocity)
    logging.debug(f"Simulation info: start_time={start_time} "
                  f"start_measurement={start_measurement} "
                  f"start_pos=[{block.position.x}, {block.position.y}] "
                  f"start_velocity=[{block.velocity.x}, {block.velocity.y}]")

    running = True
    while running:
        curr_time = round(time(), 2)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        if (not is_full and len(stop_events) > 10) or (is_full and len(collision_events) > model_cycles_amount):
            running = False

        if abs(block.velocity[0]) < SIM_PRECISION and abs(block.velocity[1]) < SIM_PRECISION:
            stop_events.append(Measurement(curr_time, block.position, block.velocity))
            logging.info(f"Block stop detected, {stop_events[-1]}")

        display.fill((65, 65, 65))
        space.debug_draw(draw_options)
        pygame.display.update()
        clock.tick(SIM_FPS)
        space.step(1 / SIM_FPS)
    pygame.quit()

    end_time = Scalar(round(time(), 2), UNIT_TIME)
    end_measurement = Measurement(end_time.value, block.position, block.velocity)
    logging.info(f"Simulation finished. duration={end_time - start_time}")
    logging.debug(f"Simulation info: end_time={end_time} "
                  f"end_measurement={end_measurement} "
                  f"detected wall-block collisions n={len(collision_events)} events={collision_events} "
                  f"detected block stops n={len(stop_events)} events={stop_events} ")

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
    logging.debug(f"Collecting cycles. stop_events={stop_events} collision_events={collision_events}")
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
            logging.debug(f"Collected cycle, {cycles[-1]}")
            cycle_i += 1
    logging.debug(f"Collected cycles, n={len(cycles)}")
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
    logging.info(f"Preparing results, stop_events={stop_events} collision_events={collision_events} is_full={is_full}")
    results = []
    cycles = collect_cycles(stop_events, collision_events)
    for cycle in cycles:
        results.append(Result.measured(cycle, is_full))
        logging.info(f"Prepared result, result={results[-1]}")
    logging.info(f"Prepared results, n={len(results)}")
    return results


def prepare_errors(measured: list[Result], model: list[Result]) -> list[Error]:
    errors = []
    for i in range(0, len(model)):
        errors.append(Error(measured[i], model[i]))
    return errors


def calculate_theoretical_model(user_input: Input) -> list[Result]:
    """
    Prepares model results based on physics formulas.
    :param user_input: Input data.
    :return: List with Result object for each cycle.
    """
    logging.debug(f"Calculating model: input={user_input}")
    g = abs(SIM_GRAVITY[1] / SIM_SCALE)
    results = [Result.model(0,
                            user_input.velocity,
                            user_input.tilt.value,
                            user_input.friction.value,
                            g,
                            False)]
    if (user_input.friction * cos(user_input.tilt.value)) / (sin(user_input.tilt.value)) >= 1:
        logging.debug(f"Not full cycle detected! result={results[0]}")
        logging.info(f"Calculated model: N={len(results)} results={results}")

    results = [Result.model(0,
                            user_input.velocity,
                            user_input.tilt.value,
                            user_input.friction.value,
                            g,
                            True)]
    logging.debug(f"Calculated model result: n={0} result={results[-1]}")
    i = 1
    while results[-1].end_velocity.value > SIM_PRECISION / SIM_SCALE:
        results.append(Result.model(i,
                                    results[-1].end_velocity,
                                    user_input.tilt.value,
                                    user_input.friction.value,
                                    g,
                                    True))
        logging.debug(f"Calculated model result: n={i} result={results[-1]}")
        i += 1

    logging.info(f"Calculated model: N={len(results)} results={results}")
    return results


def read_console() -> Input:
    """
    Reads user's input from console.
    :returns: User Input.
    """
    angle = input("Tilt of plane (rad) (0; pi/2) = ")
    friction = input("Friction coefficient (Coulomb friction) (0;inf) = ")
    mass = input("Block's mass (kg) (0;inf) = ")
    velocity = input("Starting velocity (m/s) (parallel to slope) (0;inf) = ")
    inp = Input.user(angle, mass, velocity, friction)
    logging.debug("Read user's input: ", inp)
    return inp


def main():
    print_banner()
    logging_init()

    ports = AppPorts()

    user_input = read_console()
    # user_input = Input.user("0.7854", "1", "20", "0.5")
    simulation_input = Input.simulation(user_input)

    model = calculate_theoretical_model(user_input)
    is_full = model[0].is_full

    space, block = init_space(simulation_input)
    collisions, measurements, sim_duration = simulate(space, block, simulation_input, len(model), is_full)
    measured = prepare_results(measurements, collisions, is_full)
    errors = prepare_errors(measured, model)

    ports.output_port.send_output(measured, model, errors)


main()
