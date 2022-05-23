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
from dotenv.main import DotEnv

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class EnvNames(Enum):
    CONFIG_PATH = ("_DOC_CREATION_CONFIG_PATH", str)

    @property
    def var_name(self) -> str:
        return self.value[0]

    @property
    def conversion_func(self) -> Callable:
        return self.value[1]

    def __str__(self) -> str:
        return str(self.value[0])


class EnvManager:

    def __init__(self, env_names: type[Enum] = EnvNames) -> None:
        self.env_names = env_names
        self.loaded_env_files = {}

    @property
    def all_env_names(self) -> Mapping[str, str]:
        return {k: v.var_name for k, v in self.env_names.__members__.items()}

    def add_config_path(self, config_path: Path) -> None:
        os.environ[self.env_names.CONFIG_PATH.var_name] = self.env_names.CONFIG_PATH.conversion_func(config_path)

    def load_env_file(self, env_file_path: Path) -> None:
        if env_file_path.is_file() is False:
            return {}
        dot_env = DotEnv(env_file_path)
        dot_env.set_as_environment_variables()
        self.loaded_env_files[env_file_path] = dot_env.dict()


    # region[Main_Exec]
if __name__ == '__main__':
    pass

# endregion[Main_Exec]
