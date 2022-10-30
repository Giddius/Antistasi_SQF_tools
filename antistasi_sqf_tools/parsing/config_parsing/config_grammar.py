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
import gc
import reprlib
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
import weakref
import pyparsing as ppa
# ppa.ParserElement.reset_cache()
# ppa.ParserElement.enable_packrat(1024 * 10, force=True)
# ppa.ParserElement.enable_left_recursion(1024, force=True)
from pyparsing import common as ppc


# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()
# quick_example_file = Path(r"D:\Dropbox\hobby\Modding\Programs\Github\My_Repos\Antistasi_SQF_tools\tests\example_data\example_config_files\example_memberlist_1.hpp")
# quick_example_file = Path(r"D:\Dropbox\hobby\Modding\Programs\Github\My_Repos\Antistasi_SQF_tools\tests\example_data\example_config_files\full_config_dump_w_mods.cpp")
quick_example_file = Path(r"D:\Dropbox\hobby\Modding\Programs\Github\My_Repos\Antistasi_SQF_tools\tests\example_data\example_config_files\rhs_3cb_faa_unsung_config_dump.cpp")

# quick_example_file = Path(r"D:\Dropbox\hobby\Modding\Programs\Github\My_Repos\Antistasi_SQF_tools\tests\example_data\example_config_files\cleaned_full_config_dump_w_mods.cpp")
# quick_example_file = Path(r"D:\Dropbox\hobby\Modding\Programs\Github\My_Repos\Antistasi_SQF_tools\tests\example_data\example_config_files\cleaned_rhs_3cb_faa_unsung_config_dump.cpp")

quick_example_file_text = quick_example_file.read_text(encoding='utf-8', errors='ignore')


# endregion[Constants]
class BaseElements:
    comma = ppa.Literal(",").suppress()
    colon = ppa.Literal(":").suppress()
    semi_colon = ppa.Literal(";").suppress()
    period = ppa.Literal(".").suppress()
    pipe = ppa.Literal("|").suppress()
    at = ppa.Literal("@").suppress()
    hyhphen = ppa.Literal("-").suppress()

    octothorp = ppa.Literal("#").suppress()
    tilde = ppa.Literal("~").suppress()

    plus = ppa.Literal("+").suppress()
    minus = ppa.Literal("-").suppress()
    asterisk = ppa.Literal("*").suppress()
    equals = ppa.Literal("=").suppress()

    forward_slash = ppa.Literal("/").suppress()
    back_slash = ppa.Literal("/").suppress()

    single_quote = ppa.Literal("'").suppress()
    double_quote = ppa.Literal('"').suppress()
    any_quote = single_quote | double_quote

    parentheses_open = ppa.Literal("(").suppress()
    parentheses_close = ppa.Literal(")").suppress()

    brackets_open = ppa.Literal("[").suppress()
    brackets_close = ppa.Literal("]").suppress()

    braces_open = ppa.Literal("{").suppress()
    braces_close = ppa.Literal("}").suppress()


class Ligatures:
    arrow_right = ppa.Literal("->").suppress()
    arrow_left = ppa.Literal("<-").suppress()

    big_arrow_right = ppa.Literal("-->").suppress()
    big_arrow_left = ppa.Literal("<--").suppress()


COMMA = BaseElements.comma
COLON = BaseElements.colon
SEMI_COLON = BaseElements.semi_colon
PERIOD = BaseElements.period
PIPE = BaseElements.pipe
AT = BaseElements.at
HYHPHEN = BaseElements.hyhphen
OCTOTHORP = BaseElements.octothorp
TILDE = BaseElements.tilde
PLUS = BaseElements.plus
MINUS = BaseElements.minus
ASTERISK = BaseElements.asterisk
EQUALS = BaseElements.equals
FORWARD_SLASH = BaseElements.forward_slash
BACK_SLASH = BaseElements.back_slash
SINGLE_QUOTE = BaseElements.single_quote
DOUBLE_QUOTE = BaseElements.double_quote
ANY_QUOTE = BaseElements.any_quote
PARENTHESES_OPEN = BaseElements.parentheses_open
PARENTHESES_CLOSE = BaseElements.parentheses_close
BRACKETS_OPEN = BaseElements.brackets_open
BRACKETS_CLOSE = BaseElements.brackets_close
BRACES_OPEN = BaseElements.braces_open
BRACES_CLOSE = BaseElements.braces_close


ARROW_RIGHT = Ligatures.arrow_right
ARROW_LEFT = Ligatures.arrow_left
BIG_ARROW_RIGHT = Ligatures.big_arrow_right
BIG_ARROW_LEFT = Ligatures.big_arrow_left


ppa.enable_all_warnings()

AMOUNT_CLASSES_FOUND: int = 0


def increase_classes_found():
    global AMOUNT_CLASSES_FOUND
    AMOUNT_CLASSES_FOUND += 1
    if AMOUNT_CLASSES_FOUND % 1000 == 0:
        sys.stderr.write(f"found {AMOUNT_CLASSES_FOUND!r} classes\n")
        sys.stderr.flush()


class BaseAttributeToken:
    __slots__ = ("name", "value", "_container")

    def __init__(self, name: str, value: object) -> None:
        self.name = name
        self.value = value
        self._container = None

    @property
    def container(self):
        return self._container

    def set_container(self, value):
        self._container = weakref.proxy(value)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r}, value={self.value!r})"

    def container_path(self) -> str:
        if self.container:
            return f"{self.container.container_path()}.{self.name}"
        return f"{self.name}"

    def to_json(self) -> dict[str, object]:
        return {"name": self.name, "value": self.value}


class StringAttributeToken(BaseAttributeToken):
    __slots__ = tuple()


class IntegerAttributeToken(BaseAttributeToken):
    __slots__ = tuple()


class FloatAttributeToken(BaseAttributeToken):
    __slots__ = tuple()


class ArrayAttributeToken(BaseAttributeToken):
    __slots__ = tuple()

    @classmethod
    def from_parsing_action(cls, t: ppa.ParseResults) -> "ArrayAttributeToken":

        return cls(t.attr_name, t.attr_value[0])


class ClassToken:
    __slots__ = ("name", "attributes", "classes", "parent_name", "_container", "__weakref__")

    def __init__(self, name: str, attributes: Iterable[BaseAttributeToken], classes: Iterable["ClassToken"], parent_name: str = None):
        self.name = name
        self.attributes: dict[str:"BaseAttributeToken"] = {a.name: a for a in attributes}
        self.classes: dict[str, "ClassToken"] = {c.name: c for c in classes}
        self.parent_name = parent_name
        self._container = None

    @property
    def all_classes(self) -> tuple["ClassToken"]:
        return tuple(self.classes.values())

    @property
    def all_attributes(self) -> tuple["BaseAttributeToken"]:
        return tuple(self.attributes.values())

    @property
    def container(self):
        return self._container

    def set_container(self, value):
        self._container = weakref.proxy(value)

    def set_children_container(self):
        for att in self.all_attributes:
            att.set_container(self)

        for cl in self.all_classes:
            cl.set_container(self)

    @classmethod
    def from_parsing_action(cls, t: ppa.ParseResults) -> "ArrayAttributeToken":
        parent_class_name = t[0].parent_class_name

        attributes = []
        classes = []
        for item in t[0].content.as_list():
            if isinstance(item, BaseAttributeToken):
                attributes.append(item)
            elif isinstance(item, ClassToken):
                classes.append(item)
        _instance = cls(t[0].class_name, attributes=attributes, classes=classes, parent_name=parent_class_name)
        _instance.set_children_container()
        increase_classes_found()
        return _instance

    def __getattr__(self, name: str):
        try:
            return self.attributes[name].value
        except KeyError:
            pass
        try:
            return self.attributes[name + "[]"].value
        except KeyError:
            pass
        try:
            return self.classes[name]
        except KeyError:
            pass
        raise AttributeError(name)

    def get_amount_sub_classes(self) -> int:
        sub_classes = 0
        for cl in self.all_classes:
            sub_classes += cl.get_amount_sub_classes() + 1
        return sub_classes

    def get_amount_all_attributes(self) -> int:
        attr_amount = len(self.all_attributes)
        for cl in self.all_classes:
            attr_amount += cl.get_amount_all_attributes()
        return attr_amount

    def container_path(self) -> str:
        if self.container:
            return f"{self.container.container_path()}.{self.name}"
        return f"{self.name}"

    def print_children_path(self, _indent=1) -> None:
        space_indent = _indent
        t_indend = ("    " * space_indent) + ("    " * space_indent) + "└────▻ "
        for cl in self.all_classes:
            content = f"{cl.container_path()}({cl.parent_name})" if cl.parent_name is not None else cl.container_path()
            print(f"{t_indend}{content}", flush=True)
            cl.print_children_path(_indent=_indent + 1)

    def __repr__(self) -> str:
        _out = f"{self.__class__.__name__}(name={self.name!r}, attributes={self.all_attributes!r}, classes={self.all_classes!r}, parent_name={self.parent_name!r})"
        if len(_out) > 150:
            _out = _out[:146] + "..."
        return _out

    def to_json(self) -> dict[str, object]:
        content = {"classes": [], "attributes": []}
        for cl in self.all_classes:
            content["classes"].append(cl.to_json())

        for att in self.all_attributes:
            content["attributes"].append(att.to_json())
        return {"name": self.name, "parent_name": self.parent_name, "content": content}


TOKEN_ASSIGN_MAP = {str: StringAttributeToken,
                    int: IntegerAttributeToken,
                    float: FloatAttributeToken}


def attribute_token_map(in_token):

    value = in_token.attr_value

    attr_token = TOKEN_ASSIGN_MAP[type(value)]

    return attr_token(name=in_token.attr_name, value=value)


def get_grammar() -> ppa.ParseExpression:
    CLASS_KEYWORD = ppa.Keyword("class").suppress()

    class_name = ppa.Word(ppa.alphanums + "_").set_name("class name")

    class_parent_name = ppa.Word(ppa.alphanums + "_").set_name("class parent name")

    class_parent = ppa.ungroup(BaseElements.colon + class_parent_name)

    class_content = ppa.Forward().set_name("class content")

    class_statement = ppa.Group(CLASS_KEYWORD + class_name("class_name") + ppa.Opt(class_parent, None)("parent_class_name") + BaseElements.braces_open + ppa.Group(ppa.ZeroOrMore(class_content))("content") + BaseElements.braces_close + BaseElements.semi_colon).set_parse_action(ClassToken.from_parsing_action)("class")

    attrib_name = ppa.Word(ppa.alphanums + "_")

    string_value = ppa.dbl_quoted_string.set_parse_action(ppa.remove_quotes)
    # string_attrib = (attrib_name("attr_name") + BaseElements.equals + string_value("attr_value") + BaseElements.semi_colon).set_parse_action(lambda x: StringAttributeToken(x.attr_name, x.attr_value))

    int_value = ppc.signed_integer.copy()

    # int_attrib = (attrib_name("attr_name") + BaseElements.equals + int_value("attr_value") + BaseElements.semi_colon).set_parse_action(lambda x: IntegerAttributeToken(x.attr_name, x.attr_value))

    float_value = ppc.sci_real.copy()

    # float_attrib = (attrib_name("attr_name") + BaseElements.equals + float_value("attr_value") + BaseElements.semi_colon).set_parse_action(lambda x: FloatAttributeToken(x.attr_name, x.attr_value))

    # array_attrib_name = ppa.Regex(r"[a-zA-Z0-9\_]+\[\]")
    array_attrib_name = ppa.Combine(ppa.Word(ppa.alphanums + "_") + ppa.Literal("[]"))
    array_content = ppa.Forward()
    array_value = BaseElements.braces_open + ppa.Group(ppa.Opt(ppa.delimited_list(array_content, ",", allow_trailing_delim=True)), True) + BaseElements.braces_close
    attribute_value = string_value | float_value | int_value
    attribute_statement = (attrib_name("attr_name") + BaseElements.equals + attribute_value("attr_value") + BaseElements.semi_colon).set_parse_action(attribute_token_map)

    array_content <<= (attribute_value | array_value)
    array_attrib = (array_attrib_name("attr_name") + BaseElements.equals + array_value("attr_value") + BaseElements.semi_colon).set_parse_action(ArrayAttributeToken.from_parsing_action)

    class_content <<= (attribute_statement | array_attrib | class_statement)
    class_statement = class_statement.ignore(ppa.dbl_slash_comment)
    ppa.autoname_elements()
    grammar = class_statement | attribute_statement | array_attrib
    return grammar


OUTPUT_TEMPLATE = """
start_pos: {start_pos!r}
end_post: {end_pos!r}

content: {content!r}
amount_sub_classes: {amount_sub_classes!r}
amount_all_attributes: {amount_all_attributes!r}

{separator}
"""

END_OF_FILE = object()
NAME_REGEX = re.compile(r"\s*class (?P<name>[\w\\\.\_]+)(\: *[\w\\\.\_]+)?\s*\{")


def get_top_level_classes_strings(in_string) -> tuple[str]:
    braces_count = 0

    collected_string = []

    string_gen = (c for c in in_string)

    current_char = None

    def collect_to_next_class():

        nonlocal current_char
        nonlocal braces_count
        print(f"{braces_count=}")
        while not NAME_REGEX.match(''.join(collected_string).lstrip()):
            current_char = next(string_gen, END_OF_FILE)
            if current_char is END_OF_FILE:
                break
            collected_string.append(current_char)
        if current_char == "{":
            braces_count += 1

    collect_to_next_class()

    while True:
        current_char = next(string_gen, END_OF_FILE)
        if current_char is END_OF_FILE:
            break
        collected_string.append(current_char)
        if current_char == "{":
            braces_count += 1

        if current_char == "}":
            braces_count -= 1

        if braces_count == 0 and collected_string != [] and "{" in collected_string and collected_string[-1] == ";" and collected_string[-2] == "}":
            yield ''.join(c for c in collected_string).strip()
            collected_string = []
            collect_to_next_class()


def pre_clean(in_text: str) -> str:
    escaped_quote_clean_regex = re.compile(r'\\')
    remove_outer_class_regex = re.compile(r"^\s*class bin/config.bin\s*\{")
    new_text = escaped_quote_clean_regex.sub("/", in_text)
    new_text, amount = remove_outer_class_regex.subn("", new_text)
    print(f"{amount=}", flush=True)
    if amount == 1:
        new_text = new_text.strip().removesuffix("};")
    elif amount > 1:
        print(f"remove too much {amount!r}", flush=True)
    return new_text


OUT_FOLDER = THIS_FILE_DIR.joinpath("top_level_cfg_classes")
if not OUT_FOLDER.exists():
    OUT_FOLDER.mkdir(parents=True, exist_ok=True)
for file in OUT_FOLDER.iterdir():
    if file.is_file():
        file.unlink(missing_ok=True)


def write_to_json(in_class: "ClassToken"):
    with OUT_FOLDER.joinpath(f"{in_class.name}.json").open("w", encoding='utf-8', errors='ignore') as f:
        json.dump(in_class.to_json(), f, indent=4, default=str)


def do():
    sep = "+-" * 50

    s = "-"
    e = "-"

    print("getting grammar", flush=True)
    grammar = get_grammar()
    collected_classes = []
    # grammar.set_debug(True)
    # grammar.enable_left_recursion(1024, force=True)
    pool = ThreadPoolExecutor()

    print("starting parsing\n\n", flush=True)
    for tt in grammar.scan_string(pre_clean(quick_example_file_text)):
        # for tt in ppa.OneOrMore(grammar).parse_string(pre_clean(quick_example_file_text), parse_all=True):

        _c, s, e = (tt[0], tt[1], tt[2])
        c = _c[0]
        if isinstance(c, ClassToken):
            print(f"\ncreated class {c.name!r}", flush=True)
            pool.submit(write_to_json, c)
        elif isinstance(c, BaseAttributeToken):
            print(f"\ncreated ATTRIBUTE {c.name}\n")
    pool.shutdown(wait=True)

# region[Main_Exec]


if __name__ == '__main__':
    pass
# endregion[Main_Exec]
