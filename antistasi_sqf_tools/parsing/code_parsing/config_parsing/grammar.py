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

from pyparsing import common as ppc


from antistasi_sqf_tools.code_parsing.general_parts import GeneralGrammarParts
# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]

quick_example_file = Path(r"D:\Dropbox\hobby\Modding\Programs\Github\My_Repos\Antistasi_SQF_tools\tests\example_data\example_config_files\example_memberlist_1.hpp")

quick_example_file_text = quick_example_file.read_text(encoding='utf-8', errors='ignore')


class ConfigGrammar:

    def __init__(self) -> None:
        self.general_grammar_parts: GeneralGrammarParts = GeneralGrammarParts()

    def token_factory(self, tokens):
        print(f"{tokens=}")
        print("\n")
        print(f"{tokens[0]=}")
        print("\n")
        print(f"{tokens.as_dict()=}")
        print("-" * 10)

    def _create_grammar(self) -> ppa.ParserElement:
        class_keyword = ppa.Keyword("class").suppress()
        class_name = class_keyword + ppa.Word(ppa.alphas + "_", ppa.alphanums + "_")
        class_content = ppa.Forward()
        class_token = ppa.dict_of(class_name, (self.general_grammar_parts.braces_open + class_content + self.general_grammar_parts.braces_close + self.general_grammar_parts.semi_colon)).set_parse_action(self.token_factory)

        attrib_name = ppa.Word(ppa.alphas + "_", ppa.alphanums + "_")
        string_value = ppa.dbl_quoted_string.set_parse_action(ppa.remove_quotes)

        array_attrib_name = ppa.Word(ppa.alphas + "_", ppa.alphanums + "_" + "[]")
        array_value = self.general_grammar_parts.braces_open + ppa.Group(ppa.Optional(ppa.delimited_list(ppc.integer, ","))) + self.general_grammar_parts.braces_close

        string_attrib = ppa.dict_of(attrib_name, self.general_grammar_parts.equals_sign + string_value + self.general_grammar_parts.semi_colon)
        array_attrib = ppa.dict_of(array_attrib_name, self.general_grammar_parts.equals_sign + array_value + self.general_grammar_parts.semi_colon)
        class_content <<= ppa.Group(ppa.ZeroOrMore(class_token | string_attrib | array_attrib))("content")

        class_token.ignore(ppa.dbl_slash_comment)
        return class_token


# region[Main_Exec]


if __name__ == '__main__':

    x = ConfigGrammar()
    g = x._create_grammar()

    for i in g.parse_string(quick_example_file_text, parse_all=True):
        with open("arghhhh.json", "w", encoding='utf-8', errors='ignore') as f:
            json.dump(i.as_dict(), f, default=str, indent=4, sort_keys=False)


# endregion[Main_Exec]
