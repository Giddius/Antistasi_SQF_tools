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

import pyparsing as ppa
import pyparsing.common as ppc

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


SINGLE_QUOTE = ppa.Suppress("'")
DOUBLE_QUOTE = ppa.Suppress('"')

COMMA = ppa.Suppress(",")
SEMI_COLON = ppa.Suppress(";")
COLON = ppa.Suppress(":")

EQUALS_SIGN = ppa.Suppress("=")
EXCLAMATION_MARK = ppa.Suppress("!")
OCTOTHORP = ppa.Suppress("#")
BACKSLASH = ppa.Suppress("\\")
FORWARD_SLASH = ppa.Suppress("/")
GREATER_THAN = ppa.Suppress("<")
LESS_THAN = ppa.Suppress(">")
PIPE = ppa.Suppress("|")

PARENTHESES_OPEN = ppa.Suppress("(")
PARENTHESES_CLOSE = ppa.Suppress(")")
BRACKETS_OPEN = ppa.Suppress("[")
BRACKETS_CLOSE = ppa.Suppress("]")
BRACES_OPEN = ppa.Suppress("{")
BRACES_CLOSE = ppa.Suppress("}")


# region[Main_Exec]

if __name__ == '__main__':
    pass

# endregion[Main_Exec]
