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
from pyparsing.common import pyparsing_common as ppc
from antistasi_sqf_tools.code_parsing.grammar.general_parts import (SINGLE_QUOTE, DOUBLE_QUOTE, COMMA, SEMI_COLON, COLON,
                                                                    EQUALS_SIGN, EXCLAMATION_MARK, OCTOTHORP, BACKSLASH, FORWARD_SLASH, GREATER_THAN, LESS_THAN, PIPE,
                                                                    PARENTHESES_OPEN, PARENTHESES_CLOSE, BRACKETS_OPEN, BRACKETS_CLOSE, BRACES_OPEN, BRACES_CLOSE)

from antistasi_sqf_tools.code_parsing.grammar.base_data_parts import STRING, INTEGER, FLOAT, VARIABLE
import pp
# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


_ARRAY_ITEM = ppa.Forward()
_ARRAY_CONTENT = ppa.delimited_list(_ARRAY_ITEM, delim=COMMA)

ARRAY = BRACKETS_OPEN + ppa.ZeroOrMore(_ARRAY_CONTENT) + BRACKETS_CLOSE

_ARRAY_ITEM <<= STRING ^ INTEGER ^ ppa.Group(ARRAY) ^ FLOAT ^ VARIABLE


# region[Main_Exec]

if __name__ == '__main__':
    x = '["rhs_weap_hk416d10", "rhsusf_acc_nt4_black", "rhsusf_acc_anpeq15_bk", "rhsusf_acc_eotech_552", ["rhs_mag_30Rnd_556x45_Mk318_PMAG"], [], "rhsusf_acc_kac_grip"]'
    i = ARRAY.parse_string(x, parse_all=True)
    print(i)
# endregion[Main_Exec]
