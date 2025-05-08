from pathlib import Path

from clld.web.assets import environment

import cldf_meta


static_path = Path(cldf_meta.__file__).parent / 'static'

environment.append_path(
    static_path.as_posix(),
    url='/cldf_meta:static/')
environment.load_path = list(reversed(environment.load_path))
