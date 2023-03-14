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
import jinja2

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

if TYPE_CHECKING:
    from antistasi_sqf_tools.doc_creating.setup.setup_docs import DocSetuper

# endregion [Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion [Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion [Constants]


class FileCreator(ABC):

    def __init__(self,
                 relative_path: Union[str, os.PathLike, Path],
                 content: str,
                 name: Optional[str] = None) -> None:

        self.relative_path = Path(relative_path)
        self._name = name

        self.content = content

        self._setuper: "DocSetuper" = None
        self._full_path: Path = None

    @property
    def name(self) -> str:
        if self._name is None:
            return self.relative_path.name

        return self._name

    @property
    def setuper(self) -> "DocSetuper":
        return self._setuper

    @property
    def full_path(self) -> Path:
        return self._full_path

    def _set_full_path(self) -> None:
        self._full_path = self.setuper.source_dir.joinpath(self.relative_path)

    def set_setuper(self, setuper: "DocSetuper") -> Self:
        self._setuper = setuper
        self._set_full_path()

        return self

    def _ensure_path(self) -> None:
        self.full_path.parent.mkdir(exist_ok=True, parents=True)

    @abstractmethod
    def _resolve_content(self) -> str:
        ...

    def create_file(self) -> None:
        self._ensure_path()
        file_content = self._resolve_content()
        self.full_path.write_text(file_content, encoding='utf-8', errors='ignore')

    @abstractmethod
    def copy(self):
        ...

    def create(self, overwrite: bool = False) -> bool:
        if self.setuper is None:
            # todo: replace with custom error
            raise RuntimeError("Cannot create file when 'setuper' was not set.")

        if self.full_path.exists() and overwrite is False:
            return False

        self.create_file()
        return True


class TemplateFileCreator(FileCreator):

    def __init__(self,
                 relative_path: Union[str, os.PathLike, Path],
                 content: Optional[str] = None,
                 name: Optional[str] = None,
                 extra_template_vars: dict[str, object] = None) -> None:
        super().__init__(relative_path=relative_path, content=content, name=name)

        self._template_env: jinja2.Environment = None

        self._template_vars: dict[str, object] = None
        self.extra_template_vars: dict[str, object] = extra_template_vars or {}

    @property
    def template_env(self) -> jinja2.Environment:
        return self._template_env

    @property
    def template_vars(self) -> dict[str, object]:
        return self._template_vars | self.extra_template_vars

    @property
    def is_template(self) -> bool:
        return True

    def copy(self):
        return self.__class__(relative_path=self.relative_path,
                              content=self.content,
                              name=self._name,
                              extra_template_vars=self.extra_template_vars)

    def _set_template_env(self) -> None:
        self._template_env = self.setuper.template_env

    def _set_template_vars(self) -> None:
        self._template_vars = {"this_file_path": self.full_path,
                               "info": self.setuper.info}

        return self._template_vars

    def _resolve_content(self) -> str:

        if self.content is not None:
            template = self.template_env.from_string(self.content)

        else:
            stem, suffix = self.name.rsplit(".", 1)
            template_name = f"{stem}.jinja_{suffix}"
            template = self.template_env.get_template(template_name)

        return template.render(self.template_vars)

    def set_setuper(self, setuper: "DocSetuper") -> Self:
        super().set_setuper(setuper)
        self._set_template_env()
        self._set_template_vars()

        return self


class FixedFileCreator(FileCreator):

    def _resolve_content(self) -> str:
        return self.content

    def copy(self):
        return self.__class__(relative_path=self.relative_path,
                              content=self.content,
                              name=self._name)


class LinkJsonFileCreator(FileCreator):

    def __init__(self,
                 relative_path: Union[str, os.PathLike, Path],
                 name: Optional[str] = None) -> None:
        super().__init__(relative_path, content=None, name=name)

    def _resolve_content(self) -> str:
        data = []
        if self.setuper.info.repo_url is not None:
            repo_item = {"name": "Github Repo",
                         "url": self.setuper.info.repo_url,
                         "description": "Github repo of this Project",
                         "aliases": ["repo"],
                         "category": "Documentation",
                         "flags": []}
            data.append(repo_item)

        return json.dumps(data, indent=4, default=str)

    def copy(self):
        return self.__class__(relative_path=self.relative_path,
                              name=self._name)


# region [Main_Exec]
if __name__ == '__main__':
    pass

# endregion [Main_Exec]
