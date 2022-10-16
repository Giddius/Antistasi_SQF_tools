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
import warnings
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
import pp

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class ThemeOptionsMap(dict):

    def _normalize_name(self, theme_name: str) -> str:
        norm_name = theme_name.casefold()
        norm_name = norm_name.replace("-", "_")

        return norm_name

    def __setitem__(self, key: str, value: "ThemeSpecificOptions") -> None:
        super().__setitem__(self._normalize_name(key), value)

    def __getitem__(self, key: str) -> "ThemeSpecificOptions":
        return super().__getitem__(self._normalize_name(key))

    def add_options(self, options: "ThemeSpecificOptions") -> None:
        self[options.theme_name] = options


_theme_options: ThemeOptionsMap[str, "ThemeSpecificOptions"] = ThemeOptionsMap()


class ThemeSpecificOptions:
    __slots__ = ("_theme_name", "html_theme_path", "html_theme_options", "html_sidebars", "pygments_style", "html_context")
    _default_pygments_style: str = "dracula"

    def __init__(self,
                 theme_name: str,
                 *,
                 html_theme_path: list[Union[str, os.PathLike]] = None,
                 html_theme_options: dict[str, Any] = None,
                 html_sidebars: dict[str, list[str]] = None,
                 pygments_style: str = None,
                 html_context: dict[str, Any] = None) -> None:
        self._theme_name = theme_name
        self.html_theme_path = html_theme_path
        self.html_theme_options = html_theme_options
        self.html_sidebars = html_sidebars
        self.pygments_style = pygments_style or self._default_pygments_style
        self.html_context = html_context

    @property
    def theme_name(self) -> str:
        return self._theme_name

    def apply_html_theme_path(self, global_data: dict[str, object]) -> dict[str, object]:
        if self.html_theme_path is None:
            return global_data

        if "html_theme_path" not in global_data:
            global_data["html_theme_path"] = self.html_theme_path

        else:
            global_data["html_theme_path"] += self.html_theme_path

        return global_data

    def apply_html_theme_options(self, global_data: dict[str, object]) -> dict[str, object]:
        if self.html_theme_options is None:
            return global_data

        if "html_theme_options" not in global_data:
            global_data["html_theme_options"] = self.html_theme_options
        else:
            global_data["html_theme_options"] |= self.html_theme_options
        return global_data

    def apply_html_sidebars(self, global_data: dict[str, object]) -> dict[str, object]:
        if self.html_sidebars is None:
            return global_data

        if "html_sidebars" not in global_data:
            global_data["html_sidebars"] = self.html_sidebars

        else:
            for key, values in self.html_sidebars.items():
                if key not in global_data["html_sidebars"]:
                    global_data["html_sidebars"][key] = values

                else:
                    global_data["html_sidebars"][key] += values
        return global_data

    def apply_pygments_style(self, global_data: dict[str, object]) -> dict[str, object]:
        global_data["pygments_style"] = self.pygments_style
        return global_data

    def apply_html_context(self, global_data: dict[str, object]) -> dict[str, object]:
        if self.html_context is None:
            return global_data

        if "html_context" not in global_data:
            global_data["html_context"] = self.html_context

        else:
            global_data["html_context"] |= self.html_context
        return global_data

    def __call__(self, global_data: dict[str, object]) -> dict[str, object]:

        mod_global_data = global_data.copy()

        for meth in [self.apply_html_theme_path, self.apply_html_theme_options, self.apply_html_sidebars, self.apply_pygments_style, self.apply_html_context]:

            mod_global_data = meth(mod_global_data)

        global_data.update(mod_global_data)
        return global_data

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(theme_name:{self.theme_name!r})'


def theme_specific_option(theme_name: str,
                          *,
                          html_theme_path: list[Union[str, os.PathLike]] = None,
                          html_theme_options: dict[str, Any] = None,
                          html_sidebars: dict[str, list[str]] = None,
                          pygments_style: str = None,
                          html_context: dict[str, Any] = None,
                          klass: type[ThemeSpecificOptions] = ThemeSpecificOptions) -> ThemeSpecificOptions:

    instance = klass(theme_name, html_theme_path=html_theme_path, html_theme_options=html_theme_options, html_sidebars=html_sidebars, pygments_style=pygments_style, html_context=html_context)
    _theme_options.add_options(instance)
    return instance


def apply_theme_specific_option(global_data: dict[str, object]) -> dict[str, object]:
    try:
        theme_name = global_data["html_theme"]
        options = _theme_options[theme_name]
        return options(global_data=global_data)
    except KeyError:
        warnings.warn(f"No theme-specific-options found for theme: {theme_name!r}.")
        return global_data


# region[Main_Exec]
if __name__ == '__main__':
    x = theme_specific_option("Groundwork", pygments_style="wuff")
    html_theme = "groundwork"
    pp(globals())

    print("\n" + "-" * 50 + "\n")

    apply_theme_specific_option(globals())
    pp(globals())

# endregion[Main_Exec]
