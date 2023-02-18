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

import subprocess
import inspect

from time import sleep, process_time, process_time_ns, perf_counter, perf_counter_ns
from io import BytesIO, StringIO
from abc import ABC, ABCMeta, abstractmethod
from copy import copy, deepcopy
from enum import Enum, Flag, auto, unique
from pprint import pprint, pformat
from pathlib import Path
from string import Formatter, digits, printable, whitespace, punctuation, ascii_letters, ascii_lowercase, ascii_uppercase
from timeit import Timer
from typing import (TYPE_CHECKING, TypeVar, TypeGuard, TypeAlias, Final, TypedDict, Generic, Union, Optional, ForwardRef, final,
                    no_type_check, no_type_check_decorator, overload, get_type_hints, cast, Protocol, runtime_checkable, NoReturn, NewType, Literal, AnyStr, IO, BinaryIO, TextIO, Any)
from collections import Counter, ChainMap, deque, namedtuple, defaultdict
from collections.abc import (AsyncGenerator, AsyncIterable, AsyncIterator, Awaitable, ByteString, Callable, Collection, Container, Coroutine, Generator,
                             Hashable, ItemsView, Iterable, Iterator, KeysView, Mapping, MappingView, MutableMapping, MutableSequence, MutableSet, Reversible, Sequence, Set, Sized, ValuesView)
from zipfile import ZipFile, ZIP_LZMA
from datetime import datetime, timezone, timedelta
from tempfile import TemporaryDirectory
from textwrap import TextWrapper, fill, wrap, dedent, indent, shorten
from functools import wraps, partial, lru_cache, singledispatch, total_ordering, cached_property, cache
from contextlib import contextmanager, asynccontextmanager, nullcontext, closing, ExitStack, suppress
from statistics import mean, mode, stdev, median, variance, pvariance, harmonic_mean, median_grouped
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, Future, wait, as_completed, ALL_COMPLETED, FIRST_EXCEPTION, FIRST_COMPLETED

from yarl import URL
if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

if TYPE_CHECKING:
    from .external_link_collection import ExternalLinkCategory

# endregion [Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion [Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion [Constants]


TARGET_STRING_TYPE = Literal["_blank", "_self", "_parent", "_top", "SAME_TAP", "NEW_TAP", "SAME_FRAME", "PARENT_FRAME"]


class LinkTarget(Enum):
    SAME_TAP = "_top"
    NEW_TAP = "_blank"
    SAME_FRAME = "_self"
    PARENT_FRAME = "_parent"

    @classmethod
    def _missing_(cls, value: object) -> Any:
        if isinstance(value, str):
            mod_value = value.casefold()
            for member in cls:
                if member.name.casefold() == mod_value:
                    return member
                if member.value.casefold() == mod_value:
                    return member
                if member.value.casefold().removeprefix("_") == mod_value:
                    return member

        return super()._missing_(value)

    @property
    def html_value(self) -> str:
        return str(self.value)


class ExternalLink:

    default_target_attribute: LinkTarget = LinkTarget.NEW_TAP

    def __init__(self,
                 name: str,
                 url: Union[str, URL],
                 aliases: Iterable[str] = None,
                 position: int = None,
                 description: str = None,
                 target: Union[TARGET_STRING_TYPE, LinkTarget] = None,
                 flags: Iterable[str] = None) -> None:
        self.name = name
        self.url = URL(url)
        self.aliases: set[str] = set(aliases) if aliases else set()
        self.position = position
        self.description = description
        self.target_attribute: Optional[LinkTarget] = LinkTarget(target) if target is not None else self.default_target_attribute
        self.category: "ExternalLinkCategory" = None
        self.flags = set(flags) if flags is not None else set()

    def _add_default_aliases(self) -> None:
        self.aliases.add(self.name.replace(" ", "_"))
        self.aliases.add(self.name.replace("-", "_"))

    @classmethod
    def set_default_target_attribute(cls, target: Union[TARGET_STRING_TYPE, LinkTarget]) -> None:
        cls.default_target_attribute = LinkTarget(target)

    @property
    def raw_url(self) -> str:
        return str(self.url)

    def __hash__(self) -> int:
        return sum(hash(attr) for attr in [self.url])

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r}, url={self.url!r}, aliases={self.aliases!r}, position={self.position!r},  description={self.description!r})"


# region [Main_Exec]
if __name__ == '__main__':
    pass
# endregion [Main_Exec]
