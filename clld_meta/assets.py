from pathlib import Path

from clld.web.assets import environment

import clld_meta


environment.append_path(
    Path(clld_meta.__file__).parent.joinpath('static').as_posix(),
    url='/clld_meta:static/')
environment.load_path = list(reversed(environment.load_path))
