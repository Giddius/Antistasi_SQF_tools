"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import os
import importlib.util
import subprocess
import shutil
from types import ModuleType
from typing import TYPE_CHECKING, Any, Union, Optional
from pathlib import Path
from functools import cached_property
from configparser import ConfigParser, NoOptionError, NoSectionError

# * Local Imports --------------------------------------------------------------------------------------->
from antistasi_sqf_tools.utilities import push_cwd

# * Type-Checking Imports --------------------------------------------------------------------------------->
if TYPE_CHECKING:
    from antistasi_sqf_tools.doc_creating.creator import Creator
    from antistasi_sqf_tools.doc_creating.env_handling import EnvManager

# endregion [Imports]


# region [Logging]


# endregion [Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion [Constants]


CONFIG_FILE_NAME = "generate_config.ini"

GIT_EXE = shutil.which('git.exe')


def main_dir_from_git(cwd: Union[str, os.PathLike, Path] = None) -> Optional[Path]:
    if GIT_EXE is None:
        raise RuntimeError("Unable to find 'git.exe'. Either Git is not installed or not on the Path.")
    cmd = subprocess.run([GIT_EXE, "rev-parse", "--show-toplevel"], capture_output=True, text=True, shell=True, check=True, cwd=cwd)
    main_dir = Path(cmd.stdout.rstrip('\n'))
    if main_dir.is_dir() is False:
        raise FileNotFoundError('Unable to locate main dir of project')
    return main_dir


def find_config_file_from_git_base(file_name: str, cwd: Union[str, os.PathLike, Path] = None) -> Optional[Path]:
    try:
        git_base_dir = main_dir_from_git(cwd=cwd)
    except (RuntimeError, FileNotFoundError):
        return None

    exclude_folders = {".venv",
                       ".vscode",
                       ".git",
                       ".pytest_cache",
                       "__pycache__"}

    for dirname, folderlist, filelist in os.walk(git_base_dir, topdown=True):
        folderlist[:] = [d for d in folderlist if d not in exclude_folders]
        for file in filelist:
            if file == file_name:
                return Path(dirname, file).resolve()


def find_config_file(file_name: str, start_dir: Union[str, os.PathLike] = None) -> Optional[Path]:
    file_name = file_name.casefold()
    start_dir = Path.cwd() if start_dir is None else Path(start_dir).resolve()

    def find_in_dir(current_dir: Path, last_dir: Path = None) -> Optional[Path]:
        if last_dir is not None and last_dir == current_dir and len(current_dir.parts) == 1:
            raise FileNotFoundError(f"Unable to locate the file {file_name!r} in the folder {start_dir.as_posix()!r} or any of its parent folders.")

        for file in current_dir.iterdir():
            if file.is_file() is False:
                continue
            if file.name.casefold() == file_name:
                return file.resolve()

        return find_in_dir(current_dir.parent, last_dir=current_dir)
    try:
        config_file = find_in_dir(start_dir, last_dir=None)
    except FileNotFoundError:
        config_file = find_config_file_from_git_base(file_name=file_name, cwd=start_dir)

    return config_file


def get_sphinx_config(source_folder: Path) -> ModuleType:
    with push_cwd(source_folder):
        spec = importlib.util.spec_from_file_location("conf", source_folder.joinpath("conf.py"))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module


class DocCreationConfig(ConfigParser):

    def __init__(self, file_path: Union[str, os.PathLike], env_manager: "EnvManager"):
        super().__init__()
        self.env_manager = env_manager
        self._path = Path(file_path).resolve()

    def setup(self) -> "DocCreationConfig":
        self.read(self.path, encoding="utf-8")
        self.env_manager.set_env("CONFIG_PATH", self.path)
        return self

    @property
    def path(self) -> Path:
        return self._path

    @property
    def folder(self) -> Path:
        return self.path.parent

    @cached_property
    def local_options(self) -> dict[str, Any]:
        return self.get_local_options()

    def get_local_options(self) -> dict[str, Any]:
        section_name = "local"
        _out = {"auto_open": self.getboolean(section_name, "auto_open", fallback=False),
                "use_private_browser": self.getboolean(section_name, "use_private_browser", fallback=True),
                "browser_for_html": self.get(section_name, "browser_for_html", fallback="firefox"),
                "env_file_to_load": self.get_env_file_to_load(),
                "preload_external_files": self.getboolean(section_name, "preload_external_files", fallback=False),
                "create_top_level_index_link": self.getboolean(section_name, "create_top_level_index_link", fallback=False)}
        return _out

    def get_source_dir(self, creator: "Creator") -> Path:
        section = f"building_{creator.builder_name.casefold()}" if creator.builder_name is not None else "building"
        key = "source_dir"

        try:
            source_dir = self.get(section, key)
        except (NoSectionError, NoOptionError):
            source_dir = None

        if source_dir in {None, ""}:
            source_dir = self.get("building", "source_dir")

        return self.folder / source_dir

    def get_output_dir(self, creator: "Creator") -> Path:
        section = f"building_{creator.builder_name.casefold()}" if creator.builder_name is not None else "building"
        key = "output_dir"
        try:
            output_dir = self.get(section, key)
        except (NoSectionError, NoOptionError):
            output_dir = None

        if output_dir in {None, ""}:
            output_dir = self.get("building", "output_dir")

        output_dir = output_dir.replace("<builder_name>", creator.builder_name.casefold())

        return self.folder / output_dir

    def get_release_output_dir(self) -> Path:
        output_dir = self.get("release", "output_dir")
        return self.folder / output_dir

    def get_release_source_dir(self) -> Path:
        source_dir = self.get("release", "source_dir")
        return self.folder / source_dir

    def get_release_builder_name(self) -> str:
        return self.get("release", "builder_name", fallback="html")

    def get_create_top_level_index_link(self) -> bool:
        return self.getboolean("release", "create_top_level_index_link", fallback=False)

    def get_env_file_to_load(self) -> Path:
        rel_path = self.get("local", "env_file_to_load", fallback=".env")
        return self.folder.joinpath(rel_path)

    def __repr__(self) -> str:

        return f'{self.__class__.__name__}(file_path={self.path.as_posix()!r})'


# region [Main_Exec]
if __name__ == '__main__':
    y = DocCreationConfig(find_config_file("generate_config.ini", r"D:\Dropbox\hobby\Modding\Programs\Github\My_Repos\A3-Antistasi-Docs\source\dev_guide"))
    print(y.get_release_output_dir())
# endregion [Main_Exec]
