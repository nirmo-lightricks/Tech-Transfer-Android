# Copyright (c) 2019 Lightricks. All rights reserved.
# Created by Noam Freeman.

import os
from glob import glob

module_marker_file = "build.gradle"


def get_module_dirs(a_dir):
    search_path = os.path.join(a_dir, '**/', module_marker_file)
    marker_files = glob(search_path, recursive=True)
    module_dirs = (os.path.dirname(mf) for mf in marker_files)

    return module_dirs
