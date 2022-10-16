"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import os
import sys
import json
import pickle
import shutil
import subprocess
from typing import Union, TYPE_CHECKING
from pathlib import Path
from tempfile import TemporaryDirectory
from traceback import format_tb
import importlib.util
# * Third Party Imports --------------------------------------------------------------------------------->
from sphinx.cmd.build import main as sphinx_build

# * Local Imports --------------------------------------------------------------------------------------->
from antistasi_sqf_tools.doc_creating.env_handling import EnvManager
from antistasi_sqf_tools.doc_creating.config_handling import DocCreationConfig, get_sphinx_config
from antistasi_sqf_tools.doc_creating.utils.preload_files import FileToPreload
from antistasi_sqf_tools.doc_creating.isolated_build_env import TempSourceDir, TempTargetDir, IsolatedBuildEnvironment
from antistasi_sqf_tools.doc_creating.preprocessing.preprocessor import PreProcessor
from antistasi_sqf_tools import CONSOLE
from requests import HTTPError


# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]python -m fastero


class StdOutModifier:
    originial_std_out = sys.stdout

    def __init__(self) -> None:
        self.output_dir = None

    def set_output_dir(self, output_dir: Path):
        self.output_dir = output_dir

    def write(self, s: str):
        if s.startswith("The HTML pages are in"):
            self.__class__.originial_std_out.write(f"<original_text> {s!r}")
            s = f"The HTML pages are in {self.output_dir.as_posix()!r}.\n"

        self.__class__.originial_std_out.write(s)

    def __getattr__(self, name: str):
        return getattr(self.__class__.originial_std_out, name)

    def __enter__(self):
        sys.stdout = self
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout = self.__class__.originial_std_out


def _each_part_alphabetical_length(in_label: str):

    try:
        file, section = in_label.split(":")
    except ValueError:
        file = in_label
        section = ""

    file_parts = file.split("/")

    _out = []
    for part in file_parts:
        _out.append(part)
        _out.append(len(part))
    _out.append(section)
    return tuple(_out)


LABEL_SORT_KEY_FUNCTIONS = {'parts-alphabetical-length': _each_part_alphabetical_length}


class Creator:
    label_sort_key = "parts-alphabetical-length"
    env_manager = EnvManager()

    def __init__(self, config_file: Union[str, os.PathLike], builder_name: str, base_folder: Union[str, os.PathLike] = None) -> None:
        self.builder_name = builder_name
        self.base_folder = Path(config_file).resolve().parent if base_folder is None else Path(base_folder).resolve()
        self.config = DocCreationConfig(config_file, env_manager=self.env_manager).setup()

        self.is_release = False
        if self.builder_name == "release":
            self.is_release = True
            self.builder_name = self.config.get_release_builder_name()
        self.env_manager.set_env("IS_RELEASE", self.is_release)
        self.console = CONSOLE
        self._build_env: IsolatedBuildEnvironment = None

    def post_build(self):

        def open_in_browser(browser_name: str, file_path: Path):
            browser_name = browser_name.strip().casefold()
            if browser_name == "firefox":
                args = ["firefox", "-private-window"]

            if browser_name == "chrome":
                args = ["chrome", "--incognito"]

            args.append(file_path.resolve().as_uri())

            subprocess.run(args, text=True, start_new_session=True, check=False, shell=False, creationflags=subprocess.DETACHED_PROCESS)

        if self.config.local_options["auto_open"] is True:
            open_in_browser(self.config.local_options["browser_for_html"], self._build_env.target.original_path.joinpath("index.html"))

    def pre_build(self) -> None:

        preprocessor_conf_file = self._build_env.source.temp_path.joinpath("preprocessing_conf.py")
        if preprocessor_conf_file.exists():
            self.console.print(f"Running preprocessing with preprocessor_conf_file: {preprocessor_conf_file.as_posix()!r}")
            preprocessor = PreProcessor(source_dir=self._build_env.source.temp_path, target_dir=self._build_env.target.temp_path, preprocessing_conf_file=preprocessor_conf_file, doc_creation_config=self.config)
            preprocessor.pre_process()

    def _get_all_labels(self, build_dir: Path) -> tuple[str]:
        env_pickle_file = next(build_dir.glob("**/environment.pickle"))
        with env_pickle_file.open("rb") as f:
            dat = pickle.load(f)
        raw_labels = set(dat.domaindata['std']['labels'].keys())
        try:
            return tuple(sorted(raw_labels, key=LABEL_SORT_KEY_FUNCTIONS[self.label_sort_key]))
        except Exception as e:
            self.console.rule(f"ERROR: {e!r}", style="bold red")
            self.console.print(f"While sorting labels, encountered Error {e!r}.", style="white on red")
            self.console.print_exception()
            self.console.rule(style="bold red")
            return tuple(set(raw_labels))

    def build(self):
        self.console.rule("PRE-LOADING", style="bold")
        self.console.print(f"- Trying to load env-file {self.config.local_options['env_file_to_load'].as_posix()!r}", style="bold")
        self.env_manager.load_env_file(self.config.local_options["env_file_to_load"])
        if self.is_release is True:
            return self.release()

        self._build_env = IsolatedBuildEnvironment(source_dir=self.config.get_source_dir(self), target_dir=self.config.get_output_dir(self))
        with self._build_env:
            self.pre_build()
            # args = ["-M", self.builder_name, str(self.config.get_source_dir(self)), str(temp_build_dir)]
            meta_dir = self._build_env.target.temp_path.joinpath("meta_data")
            meta_dir.mkdir(exist_ok=True, parents=True)
            args = [str(self._build_env.source.temp_path), str(self._build_env.target.temp_path), "-b", self.builder_name]

            with StdOutModifier() as mod_std_out:
                mod_std_out.set_output_dir(self._build_env.target.original_path)
                returned_code = sphinx_build(args)
            if returned_code == 0:

                label_list = self._get_all_labels(self._build_env.target.temp_path)

                available_labels_file = self._build_env.target.original_path.joinpath("available_label.json")
                available_labels_file.parent.mkdir(exist_ok=True, parents=True)

                with available_labels_file.open("w", encoding='utf-8', errors='ignore') as f:
                    json.dump(label_list, f, indent=4, sort_keys=False, default=str)
        self.post_build()

    def release(self):
        output_dir = self.config.get_release_output_dir()
        output_dir.mkdir(exist_ok=True, parents=True)
        self.pre_build()
        with TemporaryDirectory() as temp_dir:
            temp_build_dir = Path(temp_dir).resolve()
            args = ["-M", self.builder_name, str(self.config.get_release_source_dir()), str(temp_build_dir)]
            returned_code = sphinx_build(args)
            if returned_code == 0:
                shutil.rmtree(output_dir)
                shutil.copytree(temp_build_dir / self.builder_name, output_dir, dirs_exist_ok=True)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(builder_name={self.builder_name!r}, base_folder={self.base_folder.as_posix()!r}, config={self.config!r})"

# region[Main_Exec]


if __name__ == '__main__':
    pass

# endregion[Main_Exec]
