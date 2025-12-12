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
from infrastructure.constants import VERSION


def print_banner():
    print(
        fr"""
 _____           _ _                _  ______ _                   ______          _           _   
|_   _|         | (_)              | | | ___ \ |                  | ___ \        (_)         | |  
  | | _ __   ___| |_ _ __   ___  __| | | |_/ / | __ _ _ __   ___  | |_/ / __ ___  _  ___  ___| |_ 
  | || '_ \ / __| | | '_ \ / _ \/ _` | |  __/| |/ _` | '_ \ / _ \ |  __/ '__/ _ \| |/ _ \/ __| __|
 _| || | | | (__| | | | | |  __/ (_| | | |   | | (_| | | | |  __/ | |  | | | (_) | |  __/ (__| |_ 
 \___/_| |_|\___|_|_|_| |_|\___|\__,_| \_|   |_|\__,_|_| |_|\___| \_|  |_|  \___/| |\___|\___|\__|
                                                                                _/ |              
                                                                               |__/                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 
InclinedPlaneProject v{VERSION}
All rights reserved 2025.
        """
    )
