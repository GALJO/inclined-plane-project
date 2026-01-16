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
from application.input.model.input import Input
from application.result.error import prepare_errors
from application.result.result import prepare_simulation_results, calculate_theoretical_model
from application.simulation.simulation import init_space, simulate
from infrastructure.app_ports import AppPorts
from infrastructure.catcher import catcher
from infrastructure.config.config import CONFIG
from infrastructure.config.init_config import INIT_CONFIG
from infrastructure.log.util.pre_logging import init_pre_logging
from infrastructure.print_banner import print_banner


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
    measured = prepare_simulation_results(measurements, collisions, is_full)
    errors = prepare_errors(measured, model)
    ports.output.send_output(measured, model, errors)


main()
