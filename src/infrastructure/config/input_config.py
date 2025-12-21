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
class InputConfig:
    """ """
    def __init__(self, port: str,
                 min_tilt: float | None,
                 min_mass: float | None,
                 min_vel: float | None,
                 min_friction: float | None,
                 max_tilt: float | None,
                 max_mass: float | None,
                 max_vel: float | None,
                 max_friction: float | None,
                 math_precision: int):
        self.port: str = port
        self.min_tilt: float | None = round(min_tilt, math_precision) if min_tilt is not None else None
        self.min_mass: float | None = round(min_mass, math_precision) if min_mass is not None else None
        self.min_velocity: float | None = round(min_vel, math_precision) if min_vel is not None else None
        self.min_friction: float | None = round(min_friction, math_precision) if min_friction is not None else None
        self.max_tilt: float | None = round(max_tilt, math_precision) if max_tilt is not None else None
        self.max_mass: float | None = round(max_mass, math_precision) if max_mass is not None else None
        self.max_velocity: float | None = round(max_vel, math_precision) if max_vel is not None else None
        self.max_friction: float | None = round(max_friction, math_precision) if max_friction is not None else None