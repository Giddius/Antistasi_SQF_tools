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
    key = ppa.Word(ppa.alphas) + ppa.Literal(":").suppress()

    value = ppa.Combine(ppa.ZeroOrMore(ppa.Word(unicodePrintables), stop_on=key), adjacent=False, join_string=" ")
    return ppa.dict_of(key, value)


HEADER_GRAMMAR = get_header_grammar()

HEADER_REGEX = re.compile(r"/\*(?P<text>.*?)\*/", re.DOTALL)

CATEGORY_REGEX = re.compile(r"^(?P<name>\w+)\:", re.MULTILINE)


def get_header(in_file: Path):
    header_match = HEADER_REGEX.match(in_file.read_text(encoding='utf-8', errors='ignore').strip())
    if header_match:
        category_names = []
        text = header_match.group("text")
        d = HEADER_GRAMMAR.parse_string(text, parse_all=True).as_dict()
        return d


all_head = []
for dirname, folderlist, filelist in os.walk(r"D:\Dropbox\hobby\Modding\Programs\Github\Foreign_Repos\A3-Antistasi"):
    for file in filelist:
        file_path = Path(dirname, file)
        if "UPSMON" in file_path.parts or "JeroenArsenal" in file_path.parts:
            continue
        if file_path.suffix == ".sqf":
            try:
                cat_names = get_header(file_path)
                if cat_names:
                    cat_names["file"] = file_path.as_posix()
                    all_head.append(cat_names)
            except ppa.ParseException as e:
                print(file_path.as_posix())
                print(e.explain())
                print("-" * 25)


OUT_FILE = Path("blah.md")
with OUT_FILE.open("w", encoding='utf-8', errors='ignore') as f:
    for head in all_head:
        f.write(f"### {head.pop('file')}\n\n")
        example = head.pop("Example", None)
        for k, v in head.items():
            f.write(f"#### {k}\n{v}\n\n")

        if example:
            f.write(f"#### Example\n```sqf\n{example}\n```\n\n")
        f.write("---\n\n")


# region[Main_Exec]

if __name__ == '__main__':
    pass

# endregion[Main_Exec]
