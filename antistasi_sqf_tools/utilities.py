"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import os
from typing import Union, Optional
from pathlib import Path
from contextlib import contextmanager
import shutil
import subprocess
# endregion [Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion [Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion [Constants]

GIT_EXE = shutil.which('git.exe')


def main_dir_from_git(cwd: Union[str, os.PathLike, Path] = None) -> Optional[Path]:
    if GIT_EXE is None:
        raise RuntimeError("Unable to find 'git.exe'. Either Git is not installed or not on the Path.")
    cmd = subprocess.run([GIT_EXE, "rev-parse", "--show-toplevel"], capture_output=True, text=True, shell=True, check=True, cwd=cwd)
    text = cmd.stdout.strip()
    if text:
        main_dir = Path(cmd.stdout.rstrip('\n')).resolve()

        if main_dir.exists() is False or main_dir.is_dir() is False:
            raise FileNotFoundError('Unable to locate main dir of project')

    else:
        raise FileNotFoundError('Unable to locate main dir of project')

    return main_dir


@contextmanager
def push_cwd(new_cwd: Union[str, os.PathLike]):
    previous_cwd = Path.cwd()
    new_cwd = Path(new_cwd)
    os.chdir(new_cwd)
    try:
        yield
    finally:
        os.chdir(previous_cwd)


# region [Main_Exec]

if __name__ == '__main__':
    pass

# endregion [Main_Exec]
