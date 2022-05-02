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
import importlib
import subprocess
import inspect

from time import sleep, process_time, process_time_ns, perf_counter, perf_counter_ns
from io import BytesIO, StringIO
from abc import ABC, ABCMeta, abstractmethod
from copy import copy, deepcopy
from enum import Enum, Flag, auto, unique
from time import time, sleep
from pprint import pprint, pformat
from pathlib import Path
from string import Formatter, digits, printable, whitespace, punctuation, ascii_letters, ascii_lowercase, ascii_uppercase
from timeit import Timer
from typing import TYPE_CHECKING, Union, Callable, Iterable, Optional, Mapping, Any, IO, TextIO, BinaryIO, Hashable, Generator, Literal, TypeVar, TypedDict, AnyStr
from zipfile import ZipFile, ZIP_LZMA
from datetime import datetime, timezone, timedelta
from tempfile import TemporaryDirectory
from textwrap import TextWrapper, fill, wrap, dedent, indent, shorten
from functools import wraps, partial, lru_cache, singledispatch, total_ordering, cached_property
from importlib import import_module, invalidate_caches
from contextlib import contextmanager, asynccontextmanager, nullcontext, closing, ExitStack, suppress
from statistics import mean, mode, stdev, median, variance, pvariance, harmonic_mean, median_grouped
from collections import Counter, ChainMap, deque, namedtuple, defaultdict
from urllib.parse import urlparse
from importlib.util import find_spec, module_from_spec, spec_from_file_location
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from importlib.machinery import SourceFileLoader
from configparser import ConfigParser, NoOptionError, NoSectionError

if TYPE_CHECKING:
    from antistasi_sqf_tools.doc_creating.creator import Creator

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


CONFIG_FILE_NAME = "generate_config.ini"


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

    return find_in_dir(start_dir, last_dir=None)


class DocCreationConfig(ConfigParser):

    def __init__(self, file_path: Union[str, os.PathLike]):
        super().__init__()
        self.path = Path(file_path).resolve()
        self.folder = self.path.parent
        self.read(self.path, encoding="utf-8")

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


# region[Main_Exec]
if __name__ == '__main__':
    y = DocCreationConfig(find_config_file("generate_config.ini", r"D:\Dropbox\hobby\Modding\Programs\Github\My_Repos\A3-Antistasi-Docs\source\dev_guide"))
    print(y.get_release_output_dir())
# endregion[Main_Exec]
