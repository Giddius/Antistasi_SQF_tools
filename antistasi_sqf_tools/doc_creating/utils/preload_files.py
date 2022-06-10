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
import requests
from yarl import URL
# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class FileToPreload:
    chunk_size = 250 * 1000  # KB

    def __init__(self, url: str, target_folder: str, target_name: str = None, content_modification_func: Callable[[str], str] = None) -> None:
        self.url: URL = URL(url)
        self.target_folder = target_folder
        self.target_name = target_name or self.url.name
        self.content_modification_func = content_modification_func

    @classmethod
    def set_chunk_size(cls, new_chunk_size: int):
        cls.chunk_size = new_chunk_size

    def get_full_path(self, source_dir: Path) -> Path:
        return source_dir.joinpath(self.target_folder, self.target_name).resolve()

    def get_content(self) -> str:
        content = ""
        with requests.get(self.url) as response:
            response.raise_for_status()
            for chunk in response.iter_content(self.chunk_size, decode_unicode=True):
                content += chunk
        if self.content_modification_func:
            content = self.content_modification_func(content)
        return content

    def write_content(self, content: str, source_dir: Path) -> Path:
        full_target_path = source_dir.joinpath(self.target_folder, self.target_name).resolve()
        full_target_path.parent.mkdir(exist_ok=True, parents=True)
        full_target_path.write_text(content, encoding='utf-8', errors='ignore')
        return full_target_path

    def preload(self, source_dir: Path) -> Path:
        content = self.get_content()
        return self.write_content(content=content, source_dir=source_dir)

    # region[Main_Exec]
if __name__ == '__main__':
    pass
# endregion[Main_Exec]
