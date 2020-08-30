# Copyright (c) 2019 Lightricks. All rights reserved.
# Created by Noam Freeman.
import json
from subprocess import run
from typing import List


def get_module_dirs() -> List[str]:
    command_res = run(
        ["./gradlew", "-q", "listProjects"], capture_output=True, check=True, text=True
    )
    return json.loads(command_res.stdout.splitlines()[-1])
