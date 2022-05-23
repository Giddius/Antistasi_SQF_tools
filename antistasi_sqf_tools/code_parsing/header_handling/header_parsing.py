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
import pp
import pyparsing as ppa
from pyparsing.common import pyparsing_common as ppc
import string
# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]
unicodePrintables = ''.join(chr(c) for c in range(sys.maxunicode) if not chr(c).isspace())


def get_header_grammar() -> ppa.ParserElement:
    text_chars = ''.join(char for char in ppa.unicode.Latin1.printables if char not in {" ", "\t", "\n", "\r"})
    key = ppa.line_start + ppa.Word(ppa.alphas) + ppa.Literal(":").suppress()
    text = ppa.ZeroOrMore(ppa.Word(text_chars), stop_on=key)
    value = ppa.IndentedBlock(text, recursive=True)

    return ppa.Group(key + value)


HEADER_GRAMMAR = get_header_grammar()

HEADER_REGEX = re.compile(r"/\*(?P<text>.*?)\*/", re.DOTALL)

CATEGORY_REGEX = re.compile(r"(?P<cat>^\w.*)\:", re.MULTILINE)


def find_all_split_indexes(in_text: str) -> tuple[int]:
    return [m.start("cat") for m in CATEGORY_REGEX.finditer(in_text)]


def header_split(in_text: str):

    _out = {}
    all_split_indexes = find_all_split_indexes(in_text)

    split_text = [in_text[i:j] for i, j in zip(all_split_indexes, all_split_indexes[1:] + [None])]
    for sub_text in split_text:
        key, value = sub_text.split(":", maxsplit=1)
        _out[key.strip().casefold()] = dedent('\n'.join(i for i in value.splitlines() if i.strip()))

    return _out


def get_header(in_file: Path):
    header_match = HEADER_REGEX.match(in_file.read_text(encoding='utf-8', errors='ignore').strip())
    if header_match:
        category_names = []
        text = header_match.group("text")
        cleaned_text = dedent(text.lstrip("\n"))
        res = header_split(cleaned_text)
        return res


# region[Main_Exec]
if __name__ == '__main__':
    test_file = Path(r"D:\Dropbox\hobby\Modding\Programs\Github\Foreign_Repos\A3-Antistasi\A3A\addons\core\vcomai\Functions\VCM_Functions\fn_Classname.sqf")
    pp(get_header(test_file))

# endregion[Main_Exec]
