from invoke import Result, Context, Collection
from pathlib import Path
import os
import re
from typing import Union, Any
from tomlkit.toml_document import TOMLDocument
from tomlkit.api import loads as toml_loads, dumps as toml_dumps, parse, document, key as toml_key
from tomlkit.exceptions import NonExistentKey
import subprocess
from functools import reduce
from operator import getitem, setitem

from gid_tasks import set_project, add_tasks_to_vscode, task


project = set_project(create_missing_vscode_files=True)

PATH_TYPE = Union[str, os.PathLike, Path]
THIS_FILE_DIR = Path(__file__).parent.resolve()

PYPROJECT_TOML_FILE_PATH = THIS_FILE_DIR.joinpath("pyproject.toml")


VENV_FOLDER = THIS_FILE_DIR.joinpath('.venv')
SCRIPTS_FOLDER = VENV_FOLDER.joinpath('scripts')
VENV_ACTIVATOR_PATH = SCRIPTS_FOLDER.joinpath("activate.bat")
CODE_DIR = THIS_FILE_DIR.joinpath("antistasi_sqf_tools")


class PyprojectTomlFile:

    def __init__(self, path: PATH_TYPE) -> None:
        self.path = self._validate_path(path)
        self.document: TOMLDocument = None
        self.read()

    @staticmethod
    def _validate_path(path: PATH_TYPE) -> Path:
        path = Path(path).resolve()
        if path.exists() is False:
            raise FileNotFoundError(f"The file {path.as_posix!r} does not exist.")
        if path.is_file() is False:
            raise FileNotFoundError(f"The path {path.as_posix()!r} is not a file.")
        if path.suffix.casefold() != '.toml':
            # TODO: Custom Error!
            raise RuntimeError(f"The file {path.as_posix()!r} is not a toml file.")
        return path

    def read(self) -> None:
        with self.path.open('r', encoding='utf-8', errors='ignore') as f:
            self.document = toml_loads(f.read())

    def write(self) -> None:
        with self.path.open('w', encoding='utf-8', errors='ignore') as f:
            f.write(self.document.as_string())

    def get(self, key, default=None) -> Any:
        if isinstance(key, str):
            key = key.split(".")
        item = self.document
        while key:
            try:
                item = item[key.pop(0)]
            except (KeyError, NonExistentKey):
                return default
        return item

    def set(self, key, value):
        if isinstance(key, str):
            key = key.split(".")
        last_key = key.pop(-1)
        item = self.document
        while key:
            current_key = key.pop(0)
            try:
                item = item[current_key]
            except (KeyError, NonExistentKey):
                item.add(current_key)
                item = item[current_key]

        item[last_key] = value
        self.write()


def activator_run(c: Context, command, echo=True, **kwargs) -> Result:
    with c.prefix(str(VENV_ACTIVATOR_PATH.resolve())):
        result = c.run(command, echo=echo, **kwargs)
        return result


def compile_reqs(c):
    old_cwd = Path.cwd()
    try:
        os.chdir(PYPROJECT_TOML_FILE_PATH.parent)
        pip_compile_exe = f'"{SCRIPTS_FOLDER.joinpath("pip-compile.exe").resolve()!s}"'
        output_file = THIS_FILE_DIR.joinpath("compiled_reqs.txt")
        output_file.unlink(missing_ok=True)
        options = ["--no-header", "-q", "--no-annotate", "-r", f'-o {output_file.name!s}']
        arguments = [f'"{PYPROJECT_TOML_FILE_PATH!s}"']

        full_command = pip_compile_exe + ' ' + ' '.join(options) + ' ' + ' '.join(arguments)
        activator_run(c, full_command, echo=False)

        lines = output_file.read_text(encoding='utf-8', errors='ignore').splitlines()
        pyproject = PyprojectTomlFile(PYPROJECT_TOML_FILE_PATH)
        pyproject.read()
        pyproject.set("project.dependencies", lines)
        output_file.unlink(missing_ok=True)
    finally:
        os.chdir(old_cwd)


def increment_version(increment_part="patch"):

    def iter_all_files(in_dir: Path):
        for item in in_dir.iterdir():
            if item.is_file() is True:
                yield item
            elif item.is_dir() is True:
                yield from iter_all_files(item)

    def is_version_file(in_file: Path):
        with in_file.open("r", encoding='utf-8', errors='ignore') as f:
            for line_number, line in enumerate(f):
                if line.startswith("__version__"):
                    return True

        return False

    for file in iter_all_files(CODE_DIR):
        if is_version_file(file) is True:
            version_file = file
            break
    file_text = version_file.read_text(encoding='utf-8', errors='ignore')
    version_regex = re.compile(r'__version__ ?\= ?[\'\"](?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)[\'\"]')
    match = version_regex.search(file_text)
    parts = {k: int(v) for k, v in match.groupdict().items()}
    increment_part = increment_part.casefold()
    new_parts = {}
    if increment_part == "patch":
        new_parts = {"major": parts["major"], "minor": parts["minor"], "patch": parts["patch"] + 1}

    elif increment_part == "minor":
        new_parts = {"major": parts["major"], "minor": parts["minor"] + 1, "patch": 0}

    elif increment_part == "major":
        new_parts = {"major": parts["major"] + 1, "minor": 0, "patch": 0}

    new_version_string = '.'.join(str(i) for i in new_parts.values())
    new_text = version_regex.sub('__version__ = ' + '"' + new_version_string + '"', file_text, count=1)
    version_file.write_text(new_text, encoding='utf-8', errors='ignore')
    return new_version_string


def push_all(commit_message: str, c=None):
    add_command = "git add ."
    commit_command = f'git commit -am "{commit_message}"'
    push_command = 'git push'

    if c is not None:
        c.run(add_command)
        c.run(commit_command)
        c.run(push_command)

    else:
        subprocess.run(add_command, check=True, shell=False)
        subprocess.run(commit_command, check=True, shell=False)
        subprocess.run(push_command, check=True, shell=False)


@task
def publish(c, typus="patch"):
    old_cwd = Path.cwd().resolve()
    try:
        os.chdir(PYPROJECT_TOML_FILE_PATH.parent)
        compile_reqs(c)
        version_string = increment_version(increment_part=typus)

        message_table = {"patch": "{version} Small Update and Bugfixes",
                         "minor": "{version} Small Feature Update",
                         "major": "{version} Major Release!"}
        push_all(commit_message=message_table.get(typus).format(version=version_string), c=c)
        activator_run(c, "flit publish", echo=True)
        print("\n")
        print("-" * 20)
        print("DONE!")
        print("-" * 20)
    finally:
        os.chdir(old_cwd)


add_tasks_to_vscode(project, publish)
