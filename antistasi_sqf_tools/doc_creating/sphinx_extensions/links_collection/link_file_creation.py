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
import jinja2
from yarl import URL
if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

if TYPE_CHECKING:
    from .external_link_collection import ExternalLinkCollection
    from sphinx.application import Sphinx as SphinxApplication
    from sphinx.config import Config as SphinxConfig
# endregion [Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion [Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion [Constants]

DEFAULT_TEMPLATE: str = """

Links
======


{% for category, links in data %}


{{ category.pretty_name }}
----------------------------------------------------------------

{% for link in links %}


:l:`{{ link.name }}`
    {{ link.description or  "..." }}

{% endfor %}

{% endfor %}
"""


SPHINX_DESIGN_DEFAULT_TEMPLATE = """

Links
======



{% for category, links in data %}

.. card:: {{ category.pretty_name }}
   :shadow: md


   {% for ext_link in links %}

   :l:`{{ ext_link.name }}`
      {{ ext_link.description or "..." }}


   {% endfor %}


{% endfor %}

"""


def build_link_file(app: "SphinxApplication", link_collection: "ExternalLinkCollection", template_name: str):
    with Path(app.srcdir).joinpath("links.rst").resolve().open("w", encoding='utf-8', errors='ignore') as f:
        try:
            f.write(app.builder.templates.render(template_name, {"data": link_collection.get_link_file_data()}))
        except jinja2.TemplateNotFound:
            template_string = DEFAULT_TEMPLATE
            if "sphinx_design" in app.config.extensions:
                template_string = SPHINX_DESIGN_DEFAULT_TEMPLATE
            f.write(app.builder.templates.render_string(template_string, {"data": link_collection.get_link_file_data()}))


# region [Main_Exec]
if __name__ == '__main__':
    pass
# endregion [Main_Exec]
