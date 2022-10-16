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
from importlib.util import spec_from_loader
from types import ModuleType
from antistasi_sqf_tools.utilities import push_cwd

if TYPE_CHECKING:
    from antistasi_sqf_tools.doc_creating.config_handling import DocCreationConfig
# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


def preprocessing_noop(preprocessor: "PreProcessor"):
    ...


class PreProcessor:

    def __init__(self,
                 source_dir: Path,
                 target_dir: Path,
                 preprocessing_conf_file: Path,
                 doc_creation_config: "DocCreationConfig") -> None:
        self.source_dir = source_dir
        self.target_dir = target_dir
        self.preprocessing_conf_file = preprocessing_conf_file
        self.doc_creation_config = doc_creation_config
        self._preprocessing_module: ModuleType = None

    def _load_preprocessing_file(self) -> ModuleType:
        spec = importlib.util.spec_from_file_location("preprocessing_conf", self.preprocessing_conf_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self._preprocessing_module = module

    def _load_preprocessor_options(self):
        ...

    def pre_process(self) -> None:
        with push_cwd(self.source_dir):
            self._load_preprocessing_file()
            self._load_preprocessor_options()
            getattr(self._preprocessing_module, "before_preprocess", preprocessing_noop)(self)
            getattr(self._preprocessing_module, "preprocess", preprocessing_noop)(self)
            getattr(self._preprocessing_module, "after_preprocess", preprocessing_noop)(self)

# region[Main_Exec]


if __name__ == '__main__':
    pass

# endregion[Main_Exec]
