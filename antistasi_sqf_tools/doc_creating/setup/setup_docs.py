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


from jinja2.environment import Environment
import jinja2


if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

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


@unique
class ProjectTypus(Enum):
    PYTHON = "python"
    UNKNOWN = "unknown"


class BaseDocInfoFinder(ABC):
    project_typus: ProjectTypus = None

    def __init__(self) -> None:
        self._resolved: bool = False
        self.name: str = None
        self.logo_image: Path = None


class DocSetuper(ABC):
    templates_dir: Path = THIS_FILE_DIR.joinpath("templates").resolve()

    def __init__(self,
                 source_dir: Union[str, os.PathLike, Path, None],
                 target_dir: Union[str, os.PathLike, Path, None],
                 overwrite_source: bool = False,
                 overwrite_target: bool = False,
                 overwrite_config: bool = False) -> None:
        self.template_env = self._get_template_env()
        self.overwrite_settings: dict[str, bool] = {"source": overwrite_source,
                                                    "target": overwrite_target,
                                                    "config": overwrite_config}

        self.source_dir = self._resolve_source_dir(source_dir)
        self.target_dir = self._resolve_target_dir(target_dir)

    def _get_template_env(self) -> Environment:
        return Environment(loader=jinja2.FileSystemLoader(self.templates_dir))

    @abstractmethod
    def _resolve_source_dir(self, source_dir: Union[str, os.PathLike, Path, None]) -> Path:
        ...

    @abstractmethod
    def _resolve_target_dir(self, target_dir: Union[str, os.PathLike, Path, None]) -> Path:
        ...

    @abstractmethod
    def create_source_files(self) -> dict[str, Path]:
        ...

    def create_misc_files(self) -> dict[str, Path]:
        return {}

    def create_source(self) -> list[Path]:
        self.source_dir.mkdir(exist_ok=True, parents=True)

        create_paths = [self.source_dir]

        return create_paths

    def create_target(self) -> list[Path]:
        self.target_dir.mkdir(exist_ok=True, parents=True)

        created_paths = [self.target_dir]

        return created_paths

    @abstractmethod
    def create_config_file(self) -> Path:
        ...

    def run_setup(self) -> Self:
        self.create_source()
        self.create_source_files()
        self.create_target()
        self.create_config_file()
        self.create_misc_files()

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

    def create_source_files(self) -> dict[str, Path]:
        ...

    def create_source(self) -> Path:
        ...

    def create_target(self) -> Path:
        ...

    def create_config_file(self) -> Path:
        ...

    def run_setup(self) -> Self:
        ...


# region [Main_Exec]
if __name__ == '__main__':
    pass

# endregion [Main_Exec]
