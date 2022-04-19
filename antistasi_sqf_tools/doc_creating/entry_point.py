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

import click
from antistasi_sqf_tools.doc_creating.structure_creation.structure_creator import StructureCreator, get_structure_template
# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]

CONTEXT_SETTINGS = dict(

)


@ click.group(name="antistasi_doc_creator", context_settings=CONTEXT_SETTINGS)
@ click.version_option(None, "-v", "--version", package_name="antistasi_sqf_tools", prog_name="Antistasi Doc Creator")
@click.help_option("-h", "--help")
def antistasi_doc_creator_cli():
    ...


def argument_type_folder(**kwargs):
    default_kwargs = {"exists": True, "file_okay": False, "dir_okay": True, "resolve_path": True, "writable": True, "path_type": Path}
    actual_kwargs = default_kwargs | kwargs
    return click.Path(**actual_kwargs)


def argument_type_file(**kwargs):
    default_kwargs = {"exists": True, "file_okay": True, "dir_okay": False, "resolve_path": True, "writable": True, "readable": True, "path_type": Path}
    actual_kwargs = default_kwargs | kwargs
    return click.Path(**actual_kwargs)


@ antistasi_doc_creator_cli.command()
@click.argument("project-name", required=True)
@click.argument('folder-path', type=argument_type_folder(), required=False, default=Path.cwd(), nargs=1, metavar="FOLDER_PATH")
@click.option("-t", "--template")
def create_structure(project_name, folder_path, template=None):
    """
    Creates the basic structure to start writing the documentation.
    Structure will be created in FOLDER_PATH.
    Defaults to Current Working Directory.

    """
    template_name = template or "default"
    template = get_structure_template(template_name)
    creator = StructureCreator(folder_path, project_name, template)
    creator.create()


@ antistasi_doc_creator_cli.command()
def create_structure_gui():
    ...


# region[Main_Exec]
if __name__ == '__main__':
    antistasi_doc_creator_cli(sys.argv[1:])

# endregion[Main_Exec]
