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

from gidapptools.general_helper.string_helper import StringCase, StringCaseConverter, remove_chars
from gidapptools.general_helper.path_helper import open_folder_in_explorer
from antistasi_sqf_tools.doc_creating.structure_creation.script_templates import SCRIPT_TEMPLATES_FOLDER, get_script_template
from antistasi_sqf_tools.doc_creating.structure_creation.structure_templates import STRUCTURE_TEMPLATES_FOLDER, get_structure_template, StructureTemplate
import pp
# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class StructureCreator:

    def __init__(self, parent_dir: Union[str, os.PathLike], project_name: str, structure_template: StructureTemplate) -> None:
        self._parent_dir = Path(parent_dir).resolve()
        self._project_name = project_name
        self._structure_template = structure_template

    @property
    def render_kwargs(self) -> dict[str, Any]:
        return {}

    @property
    def project_name(self) -> str:
        return self._project_name

    @property
    def parent_dir(self) -> Path:
        return self._parent_dir

    @cached_property
    def safe_project_name(self) -> str:
        safe_name = self._project_name.encode("ascii", "ignore").decode()
        safe_name = remove_chars(safe_name, "\\", "/", ":", "*", "?", '"', "<", ">", "|", "#", "%", "&", "{", "}", "$", "!", "@", "`", "+", "=")
        safe_name = StringCaseConverter.convert_to(safe_name, StringCase.SNAKE)
        safe_name = safe_name.casefold()
        return safe_name.strip()

    @cached_property
    def base_folder(self) -> Path:
        return self._parent_dir.joinpath(self.safe_project_name)

    def create_folders(self):
        self.base_folder.mkdir(exist_ok=True)
        for sub_path in self._structure_template.folder:
            self.base_folder.joinpath(sub_path).resolve().mkdir(parents=True, exist_ok=True)

    def create_files(self):
        ...

    def create_scripts(self):
        for script in self._structure_template.scripts:
            script.render(self)

    def create(self):
        self.create_folders()
        self.create_files()
        self.create_scripts()
        open_folder_in_explorer(self.base_folder)

        # region[Main_Exec]
if __name__ == '__main__':
    pa = Path.cwd()
    x = get_structure_template("default")
    y = StructureCreator(pa, "Wuff Docs", x)
    y.create()
# endregion[Main_Exec]
