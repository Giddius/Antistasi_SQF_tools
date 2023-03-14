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


def escalating_find_file(file_name: str, start_dir: Union[os.PathLike, str, Path] = None, max_escalation: int = 3) -> Path:

    file_name = file_name.casefold()
    start_dir = Path(start_dir).resolve() if start_dir is not None else Path.cwd().resolve()

    def _check_in_dir(in_dir: Path, current_escalation: int = 0) -> Optional[Path]:
        if current_escalation > max_escalation:
            return None

        if in_dir.exists() is False:
            return _check_in_dir(in_dir.parent, current_escalation=current_escalation + 1)

        for file in in_dir.iterdir():
            if file.is_dir() is True:
                continue

            if file.name.casefold() == file_name:
                return file.resolve()

        return _check_in_dir(in_dir.parent, current_escalation=current_escalation + 1)

    found_file = _check_in_dir(in_dir=start_dir, current_escalation=0)

    if found_file is None:
        raise FileNotFoundError(f"Unable to find a file with name {file_name!r} in {start_dir.as_posix()!r} or up to {max_escalation!r} folders above.")

    return found_file


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
    print(escalating_find_file("pyproject.toml", start_dir=r"D:\Dropbox\hobby\Modding\Programs\Github\My_Repos\Gid_Knowledge_Vault\source", max_escalation=10))

# endregion [Main_Exec]
