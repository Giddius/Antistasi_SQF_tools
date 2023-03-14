"""
WiP.

Soon.
"""

# region [Imports]

import os
import re
import sys
import json
import queue
import math
import base64
import pickle
import random
import shelve
import dataclasses
import shutil
import asyncio
import logging
import sqlite3
import platform

import subprocess
import inspect

from time import sleep, process_time, process_time_ns, perf_counter, perf_counter_ns
from io import BytesIO, StringIO
from abc import ABC, ABCMeta, abstractmethod
from copy import copy, deepcopy
from enum import Enum, Flag, auto, unique
from pprint import pprint, pformat
from pathlib import Path
from string import Formatter, digits, printable, whitespace, punctuation, ascii_letters, ascii_lowercase, ascii_uppercase
from timeit import Timer
from typing import (TYPE_CHECKING, TypeVar, TypeGuard, TypeAlias, Final, TypedDict, Generic, Union, Optional, ForwardRef, final,
                    no_type_check, no_type_check_decorator, overload, get_type_hints, cast, Protocol, runtime_checkable, NoReturn, NewType, Literal, AnyStr, IO, BinaryIO, TextIO, Any)
from collections import Counter, ChainMap, deque, namedtuple, defaultdict
from collections.abc import (AsyncGenerator, AsyncIterable, AsyncIterator, Awaitable, ByteString, Callable, Collection, Container, Coroutine, Generator,
                             Hashable, ItemsView, Iterable, Iterator, KeysView, Mapping, MappingView, MutableMapping, MutableSequence, MutableSet, Reversible, Sequence, Set, Sized, ValuesView)
from zipfile import ZipFile, ZIP_LZMA
from datetime import datetime, timezone, timedelta
from tempfile import TemporaryDirectory
from textwrap import TextWrapper, fill, wrap, dedent, indent, shorten
from functools import wraps, partial, lru_cache, singledispatch, total_ordering, cached_property, cache
from contextlib import contextmanager, asynccontextmanager, nullcontext, closing, ExitStack, suppress
from statistics import mean, mode, stdev, median, variance, pvariance, harmonic_mean, median_grouped
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, Future, wait, as_completed, ALL_COMPLETED, FIRST_EXCEPTION, FIRST_COMPLETED
from configparser import ConfigParser

from jinja2.environment import Environment
import jinja2
from antistasi_sqf_tools.doc_creating.setup.file_creator import FileCreator, TemplateFileCreator, FixedFileCreator, LinkJsonFileCreator
from antistasi_sqf_tools.utilities import escalating_find_file

from antistasi_sqf_tools.doc_creating.setup.templates import PLACEHOLDER_FAVICON_FILE, PLACEHOLDER_LOGO_FILE

from antistasi_sqf_tools.doc_creating.utils.string_helper import StringCase, StringCaseConverter

if sys.version_info >= (3, 11):
    from typing import Self
    import tomllib
else:
    from typing_extensions import Self
    import tomli as tomllib
if TYPE_CHECKING:
    ...

# endregion [Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion [Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()


# endregion [Constants]

RST_INDENT = "   "


def rst_header(text: str, indicator_char: str = "=", overline_too: bool = False) -> str:
    full_indicator_line = indicator_char * max(len(text) + 1, int(len(text) * 1.2))

    lines = [text, full_indicator_line]
    if overline_too is True:
        lines.insert(0, full_indicator_line)

    return '\n'.join(lines) + '\n'


def toc_tree(items: Iterable[str],
             caption: str = None,
             name: str = None,
             maxdepth: int = None,
             glob: bool = False,
             titlesonly: bool = False,
             _reversed: bool = False,
             hidden: bool = False,
             includehidden: bool = False,
             numbered: bool = False) -> str:

    lines = [".. toctree::"]
    if caption is not None:
        lines.append(f"{RST_INDENT}:caption: {caption}")

    if name is not None:
        lines.append(f"{RST_INDENT}:name: {name}")

    if maxdepth is not None:
        lines.append(f"{RST_INDENT}:maxdepth: {maxdepth}")

    for opt_name, opt_value in {"glob": glob,
                                "titlesonly": titlesonly,
                                "reversed": _reversed,
                                "hidden": hidden,
                                "includehidden": includehidden,
                                "numbered": numbered}.items():

        if opt_value is True:
            lines.append(f"{RST_INDENT}:{opt_name}:")

    lines.append("")

    for item in items:
        lines.append(f"{RST_INDENT}{item}")

    return '\n'.join(lines) + '\n'


def has_pyproject_file(in_start_dir: Union[str, os.PathLike, Path]) -> bool:
    try:
        escalating_find_file("pyproject.toml", start_dir=in_start_dir, max_escalation=5)
        return True

    except FileNotFoundError:
        return False


@unique
class ProjectTypus(Enum):
    PYTHON = "python"
    UNKNOWN = "unknown"

    @classmethod
    def determine_from_setuper(cls, setuper: "DocSetuper") -> Self:

        if has_pyproject_file(setuper.source_dir) is True:
            return cls.PYTHON

        return cls.UNKNOWN


class BaseDocInfoFinder(ABC):
    project_typus: ProjectTypus = None

    def __init__(self) -> None:
        self._resolved: bool = False

        self.name: str = None
        self.author: str = None
        self.repo_url: str = None
        self.version: str = None

        self.has_logo_image: bool = True

    @property
    def project_name(self) -> str:
        return self.name

    @property
    def author_name(self) -> str:
        return self.author

    @property
    def pretty_name(self) -> str:
        return StringCaseConverter.convert_to(self.name, StringCase.TITLE)

    @property
    def pretty_author(self) -> str:
        return StringCaseConverter.convert_to(self.author, StringCase.TITLE)

    @property
    def pretty_project_name(self) -> str:
        return StringCaseConverter.convert_to(self.project_name, StringCase.TITLE)

    @property
    def pretty_author_name(self) -> str:
        return StringCaseConverter.convert_to(self.author_name, StringCase.TITLE)

    @abstractmethod
    def resolve(self, setuper: "DocSetuper") -> Self:
        ...


class PythonDocInfoFinder(BaseDocInfoFinder):
    project_typus = ProjectTypus.PYTHON

    def __init__(self) -> None:
        super().__init__()

        self.pyproject_toml_path: Path = None
        self.pyproject_data: dict = None

    @property
    def package_name(self) -> str:
        return self.name

    def _read_pyproject_data(self) -> dict:
        with self.pyproject_toml_path.open("rb") as f:
            return tomllib.load(f)

    def _resolve_name(self) -> str:
        return self.pyproject_data["project"]["name"]

    def _resolve_author(self) -> str:
        return self.pyproject_data["project"]["authors"][0]["name"]

    def _resolve_repo_url(self) -> Optional[str]:
        try:
            return self.pyproject_data["project"]["urls"]["Source"]
        except KeyError:
            return None

    def _resolve_version(self) -> Optional[str]:
        base_dir = self.pyproject_toml_path.parent.joinpath(self.name)
        base_init = base_dir.joinpath("__init__.py")

        if match := re.search(r"^__version__\s*\=\s*[\"\'](?P<version>.*?)[\"\']", base_init.read_text(encoding='utf-8', errors='ignore'), re.MULTILINE):
            return f"{self.package_name}.__version__"

    def resolve(self, setuper: "DocSetuper") -> Self:
        if self._resolved is True:
            return self

        self.pyproject_toml_path = escalating_find_file("pyproject.toml", start_dir=setuper.source_dir, max_escalation=5)
        self.pyproject_data = self._read_pyproject_data()

        self.name = self._resolve_name()
        self.author = self._resolve_author()
        self.repo_url = self._resolve_repo_url()
        self.version = self._resolve_version()
        return self


class DocSetuper(ABC):
    _info_finder_map: dict[ProjectTypus, BaseDocInfoFinder] = {ProjectTypus.UNKNOWN: None,
                                                               ProjectTypus.PYTHON: PythonDocInfoFinder}
    templates_dir: Path = THIS_FILE_DIR.joinpath("templates").resolve()

    _files_to_create: tuple[FileCreator] = (LinkJsonFileCreator("_data/links.json"),
                                            TemplateFileCreator("index.rst"),
                                            TemplateFileCreator("conf.py"),
                                            TemplateFileCreator("glossary.rst"))
    _folder_to_create: tuple[Path] = (Path("_images"), Path("_data"), Path("_static"), Path("_templates"), Path("_static/css"), Path("_static/fonts"))

    def __init__(self,
                 source_dir: Union[str, os.PathLike, Path, None],
                 target_dir: Union[str, os.PathLike, Path, None],
                 overwrite_source: bool = False,
                 overwrite_target: bool = False,
                 overwrite_config: bool = False,
                 extra_files_to_create: Iterable[FileCreator] = None,
                 extra_folder_to_create: Iterable[Union[str, os.PathLike, Path]] = None,
                 project_typus: Union[str, ProjectTypus] = None) -> None:

        self.overwrite_settings: dict[str, bool] = {"source": overwrite_source,
                                                    "target": overwrite_target,
                                                    "config": overwrite_config}

        self.source_dir = self._resolve_source_dir(source_dir)
        self.target_dir = self._resolve_target_dir(target_dir)

        self.files_to_create = set([f.copy() for f in self._files_to_create] + [f.copy() for f in (extra_files_to_create or [])])
        self.folder_to_create = set(self._folder_to_create + tuple(extra_folder_to_create or []))
        self.project_typus = ProjectTypus(project_typus) if project_typus is not None else self.determine_project_typus()

        self.info = self.get_info_finder()
        self.template_env = self._get_template_env()

    def _get_template_env(self) -> Environment:
        env = Environment(loader=jinja2.FileSystemLoader(self.templates_dir))
        env.globals |= {"source_dir": self.source_dir,
                        "target_dir": self.target_dir,
                        "rst_header": rst_header,
                        "toc_tree": toc_tree}

        env.filters |= {"top_rst_header": partial(rst_header, indicator_char="=", overline_too=True),
                        "toc_tree": toc_tree,
                        "rst_header": rst_header}

        return env

    @abstractmethod
    def _resolve_source_dir(self, source_dir: Union[str, os.PathLike, Path, None]) -> Path:
        ...

    @abstractmethod
    def _resolve_target_dir(self, target_dir: Union[str, os.PathLike, Path, None]) -> Path:
        ...

    def create_source_files(self) -> list[Path]:
        ...

    def create_source(self) -> list[Path]:
        self.source_dir.mkdir(exist_ok=True, parents=True)

        created_paths = [self.source_dir]
        for folder in self.folder_to_create:
            full_folder_path = self.source_dir.joinpath(folder)
            full_folder_path.mkdir(parents=True, exist_ok=True)
            created_paths.append(full_folder_path)
        created_paths += self.create_source_files()
        return created_paths

    def create_target(self) -> list[Path]:
        self.target_dir.mkdir(exist_ok=True, parents=True)

        created_paths = [self.target_dir]

        return created_paths

    @abstractmethod
    def create_config_file(self) -> Path:
        ...

    def determine_project_typus(self) -> ProjectTypus:
        return ProjectTypus.determine_from_setuper(self)

    def get_info_finder(self) -> BaseDocInfoFinder:
        return self._info_finder_map.get(self.project_typus, self._info_finder_map[ProjectTypus.UNKNOWN])()

    def run_setup(self) -> Self:
        self.info.resolve(self)
        self.create_source()
        self.create_source_files()
        self.create_target()
        self.create_config_file()

        return self


class BasicDocSetuper(DocSetuper):

    def _resolve_source_dir(self, source_dir: Union[str, os.PathLike, Path, None]) -> Path:
        if source_dir is None:
            raise RuntimeError("source dir cannot be None")

        return Path(source_dir).resolve()

    def _resolve_target_dir(self, target_dir: Union[str, os.PathLike, Path, None]) -> Path:
        if target_dir is None:
            raise RuntimeError("target dir cannot be None")

        return Path(target_dir).resolve()

    def create_source_files(self) -> list[Path]:
        created_files = []
        for file in self.files_to_create:
            file.set_setuper(self)
            created = file.create(self.overwrite_settings["source"])
            if created is True:
                created_files.append(file.full_path)

        images_dir = self.source_dir.joinpath("_images")
        images_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy(PLACEHOLDER_LOGO_FILE, images_dir.joinpath("app_logo.png"))
        shutil.copy(PLACEHOLDER_FAVICON_FILE, images_dir.joinpath("app_favicon.png"))

        return created_files

    def create_config_file(self) -> Path:
        config_file_path = self.source_dir.parent.joinpath("generate_config.ini")

        config_data = {"folder": {"auto_generation": "auto_generation"},

                       "local": {"env_file_to_load": ".env",
                                 "auto_open": "yes",
                                 "use_private_browser": "no",
                                 "browser_for_html": "firefox"},

                       "building": {"output_dir": Path(os.path.relpath(self.target_dir.parent.joinpath("local_docs"), config_file_path.parent)).as_posix() + "/<builder_name>",
                                    "source_dir": os.path.relpath(self.source_dir, config_file_path.parent)},

                       "building_html": {"output_dir": Path(os.path.relpath(self.target_dir.parent.joinpath("local_docs", "html"), config_file_path.parent)).as_posix()},

                       "release": {"output_dir": Path(os.path.relpath(self.target_dir, config_file_path.parent)).as_posix(),
                                   "source_dir": Path(os.path.relpath(self.source_dir, config_file_path.parent)).as_posix(),
                                   "builder_name": "html",
                                   "create_top_level_index_link": "yes"}}

        config = ConfigParser()
        config.read_dict(config_data)
        with config_file_path.open("w", encoding='utf-8', errors='ignore') as f:
            config.write(f)
        return config_file_path


# region [Main_Exec]
if __name__ == '__main__':
    x = BasicDocSetuper(source_dir=r"D:\Dropbox\hobby\Modding\Programs\Github\My_Repos\Antistasi_SQF_tools\docs\source",
                        target_dir=r"D:\Dropbox\hobby\Modding\Programs\Github\My_Repos\Antistasi_SQF_tools\docs\html")

    # x.info = {"project_name": "The big blah".title(),
    #           }

    x.run_setup()


# endregion [Main_Exec]
