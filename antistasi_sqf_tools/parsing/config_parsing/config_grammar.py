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
from string import whitespace, ascii_letters, ascii_lowercase, ascii_uppercase, digits, punctuation, printable
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
from typing import TYPE_CHECKING, Union, Callable, Iterable, Optional, Mapping, Any, IO, TextIO, BinaryIO, Hashable, Generator, Literal, TypeVar, TypedDict, AnyStr, TypeAlias
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
from gidapptools.general_helper.timing import time_func
ppa.ParserElement.disable_memoization()
from pyparsing import common as ppc
if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

# endregion [Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion [Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion [Constants]


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
PRINT_CONSTANTLY_AMOUNT_CLASSES: bool = False
AMOUNT_CLASSES_FOUND: int = 0


def increase_classes_found(current_class=None):
    global AMOUNT_CLASSES_FOUND
    AMOUNT_CLASSES_FOUND += 1
    if AMOUNT_CLASSES_FOUND % 500 == 0:
        name = current_class.name if current_class is not None else current_class
        sys.stderr.write(f"found {AMOUNT_CLASSES_FOUND!r} classes, current-class: {name!r}\n")
        sys.stderr.flush()


class BaseAttributeToken:
    __slots__ = ("_name", "_value", "_container", "_container_path")

    def __init__(self, name: str, value: object) -> None:
        self._name: str = name
        self._value: object = value
        self._container = None
        self._container_path: str = None

    @property
    def name(self) -> str:
        return self._name

    @property
    def value(self) -> object:
        return self._value

    @property
    def container(self):
        return self._container

    def set_container(self, value):
        # self._container = weakref.proxy(value)
        self._container = value

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r}, value={self.value!r})"

    def get_container_path(self) -> str:
        if self.container is not None:
            return f"{self.container.container_path}.{self.name}"
        return f"{self.name}"

    @property
    def container_path(self) -> str:
        if self._container_path is None:
            self._container_path = self.get_container_path()

        return self._container_path

    def get_parents(self) -> tuple[Self]:
        def _recurse_parent(in_token: Self) -> Generator[Self, None, None]:
            if in_token.container is not None:
                yield in_token.container
                yield from _recurse_parent(in_token.container)

        return tuple(_recurse_parent(self))

    def to_json(self) -> dict[str, object]:
        return {"name": self.name, "value": self.value}

    def __hash__(self) -> int:

        _hash = hash(self.name) + hash(self.container)

        return _hash


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


class MacroAttributeToken(BaseAttributeToken):
    __slots__ = tuple()


class MacroString(str):
    ...


class StringTablePlaceholderAttributeToken(BaseAttributeToken):
    __slots__ = tuple()


class StringTablePlaceholderString(str):
    ...


class ClassToken:
    __slots__ = ("name", "attributes", "classes", "parent_name", "parent", "_container", "__weakref__", "_container_path")

    def __init__(self, name: str, attributes: Iterable[BaseAttributeToken], classes: Iterable["ClassToken"], parent_name: str = None):
        self.name = name
        self.attributes: dict[str:"BaseAttributeToken"] = {a.name: a for a in attributes}
        self.classes: dict[str, "ClassToken"] = {c.name: c for c in classes}
        self.parent_name = parent_name
        self.parent: "ClassToken" = None
        self._container = None
        self._container_path: str = None

    def __hash__(self) -> int:
        return hash(self.name) + hash(self.parent_name) + hash(self.container_path())

    @property
    def all_classes(self) -> tuple["ClassToken"]:
        return tuple(self.classes.values())

    @property
    def all_attributes(self) -> tuple["BaseAttributeToken"]:
        return tuple(self.attributes.values())

    @property
    def container(self):
        return self._container

    def find_parent(self, all_classes: Iterable["ClassToken"]) -> Optional["ClassToken"]:
        parent = next((c for c in all_classes if c.name == self.parent_name), None)
        self.set_parent(parent)
        for cl in self.all_classes:
            cl.find_parent(all_classes)
        return parent

    def set_parent(self, parent: "ClassToken") -> None:
        if parent is None:
            return
        self.parent = parent
        for attr in self.parent.all_attributes:
            if attr.name not in self.attributes:
                self.attributes[attr.name] = attr

    def set_container(self, value):
        self._container = value

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

    def get_container_path(self) -> str:
        if self.container is not None:
            return f"{self.container.container_path}.{self.name}"
        return f"{self.name}"

    @property
    def container_path(self) -> str:
        if self._container_path is None:
            self._container_path = self.get_container_path()

        return self._container_path

    def get_parents(self) -> tuple[Self]:
        def _recurse_parent(in_class_token: Self) -> Generator[Self, None, None]:
            if in_class_token.container is not None:
                yield in_class_token.container
                yield from _recurse_parent(in_class_token.container)

        return tuple(_recurse_parent(self))

    def print_children_path(self, _indent=1) -> None:
        space_indent = _indent
        t_indend = ("    " * space_indent) + ("    " * space_indent) + "└────▻ "
        for cl in self.all_classes:
            content = f"{cl.container_path()}({cl.parent_name})" if cl.parent_name is not None else cl.container_path()
            print(f"{t_indend}{content}", flush=True)
            cl.print_children_path(_indent=_indent + 1)

    def __repr__(self) -> str:

        _out = f"{self.__class__.__name__}(name={self.name!r}, parent_name={self.parent_name!r}, container_path={self.container_path!r})"

        return _out

    def to_json(self) -> dict[str, object]:
        content = {"classes": [], "attributes": []}
        for cl in self.all_classes:
            content["classes"].append(cl.to_json())

        for att in self.all_attributes:
            content["attributes"].append(att.to_json())
        return {"name": self.name, "parent_name": self.parent_name, "content": content}


TOKEN_TYPE: TypeAlias = Union[BaseAttributeToken, ClassToken]


class ConfigParsingResult:
    __slots__ = ("tokens", "_all_tokens")

    def __init__(self,
                 tokens: Iterable[TOKEN_TYPE]) -> None:
        self.tokens: dict[str:TOKEN_TYPE] = {t.name: t for t in tokens}
        self._all_tokens: tuple[TOKEN_TYPE] = None

    @classmethod
    def from_parser_result(cls, in_parser_result: ppa.ParseResults) -> Self:
        return cls(in_parser_result.as_list())

    def __getitem__(self, key: str) -> TOKEN_TYPE:
        return self.tokens[key]

    @property
    def all_tokens(self) -> set[TOKEN_TYPE]:
        if self._all_tokens is None:
            self._all_tokens = self._get_all_tokens()

        return self._all_tokens

    def _get_all_tokens(self) -> tuple[TOKEN_TYPE]:

        def _get_child_tokens(in_class_token: ClassToken) -> Generator[TOKEN_TYPE, None, None]:
            for child_attribute in in_class_token.all_attributes:
                yield child_attribute
            for child_class in in_class_token.all_classes:
                yield child_class
                yield from _get_child_tokens(child_class)

        _out = []

        for token in self.tokens.values():
            _out.append(token)
            if isinstance(token, ClassToken):

                _out.extend(_get_child_tokens(token))

        return tuple(_out)


TOKEN_ASSIGN_MAP = {str: StringAttributeToken,
                    int: IntegerAttributeToken,
                    float: FloatAttributeToken,
                    MacroString: MacroAttributeToken,
                    StringTablePlaceholderString: StringTablePlaceholderAttributeToken}


def attribute_token_map(in_token: ppa.ParseResults):

    value = in_token.attr_value

    attr_token = TOKEN_ASSIGN_MAP[type(value)]

    return attr_token(name=in_token.attr_name, value=value)


def to_macro_string(s, l, t):
    return MacroString(t[0])


def to_stringtable_string(s, l, t):
    return StringTablePlaceholderString(t[0])


def get_grammar(allow_macro_values: bool = True) -> ppa.ParseExpression:
    CLASS_KEYWORD = ppa.Keyword("class").suppress()

    class_name = ppa.Word(ppa.alphanums + "_").set_name("class name")

    class_parent_name = ppa.Word(ppa.alphanums + "_").set_name("class parent name")

    class_parent = ppa.ungroup(BaseElements.colon + class_parent_name)

    class_content = ppa.Forward().set_name("class content")

    class_statement = ppa.Group(CLASS_KEYWORD + class_name("class_name") + ppa.Opt(class_parent, None)("parent_class_name") + BaseElements.braces_open + ppa.Group(ppa.ZeroOrMore(class_content))("content") + BaseElements.braces_close + BaseElements.semi_colon).set_parse_action(ClassToken.from_parsing_action)("class")

    attrib_name = ppa.Word(ppa.alphanums + "_")

    string_value = ppa.dbl_quoted_string.set_parse_action(ppa.remove_quotes)

    int_value = ppc.signed_integer.copy()

    float_value = ppc.sci_real.copy()

    if allow_macro_values is True:
        macro_value = ppa.Combine(ppa.Word(ascii_uppercase) + ppa.Regex(r"\(.*?\)")).set_parse_action(to_macro_string)

    stringtable_placeholder_value = ppa.Word(init_chars="$", body_chars=ppa.alphanums + "_").set_parse_action(to_stringtable_string)

    array_attrib_name = ppa.Combine(ppa.Word(ppa.alphanums + "_") + ppa.Literal("[]"))
    array_content = ppa.Forward()
    array_value = BaseElements.braces_open + ppa.Group(ppa.Opt(ppa.delimited_list(array_content, ",", allow_trailing_delim=True)), True) + BaseElements.braces_close

    if allow_macro_values is True:
        attribute_value = string_value | float_value | int_value | macro_value | stringtable_placeholder_value
    else:
        attribute_value = string_value | float_value | int_value | stringtable_placeholder_value

    attribute_statement = (attrib_name("attr_name") + BaseElements.equals + attribute_value("attr_value") + BaseElements.semi_colon).set_parse_action(attribute_token_map)

    array_content <<= (attribute_value | array_value)
    array_attrib = (array_attrib_name("attr_name") + BaseElements.equals + array_value("attr_value") + BaseElements.semi_colon).set_parse_action(ArrayAttributeToken.from_parsing_action)

    class_content <<= (class_statement | attribute_statement | array_attrib)
    class_statement = class_statement.ignore(ppa.dbl_slash_comment)

    ppa.autoname_elements()
    grammar = class_statement | attribute_statement | array_attrib

    # grammar.enable_packrat()
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

# for file in OUT_FOLDER.iterdir():
#     if file.is_file():
#         file.unlink(missing_ok=True)


def write_to_json(in_class: "ClassToken"):
    if not OUT_FOLDER.exists():
        OUT_FOLDER.mkdir(parents=True, exist_ok=True)
    with OUT_FOLDER.joinpath(f"{in_class.name}.json").open("w", encoding='utf-8', errors='ignore') as f:
        json.dump(in_class.to_json(), f, indent=4, default=str)


class _ConfigGrammar:
    __slots__ = ("_grammar", "_non_macro_grammar", "_parse_string_grammar", "_parse_string_non_macro_grammar")

    def __init__(self) -> None:
        self._grammar: ppa.ParserElement = None
        self._non_macro_grammar: ppa.ParserElement = None
        self._parse_string_grammar: ppa.ParserElement = None
        self._parse_string_non_macro_grammar: ppa.ParserElement = None

    @property
    def grammar(self) -> ppa.ParserElement:
        if self._grammar is None:
            self._grammar = get_grammar(allow_macro_values=True)
        return self._grammar

    @property
    def non_macro_grammar(self) -> ppa.ParserElement:
        if self._non_macro_grammar is None:
            self._non_macro_grammar = get_grammar(allow_macro_values=False)
        return self._non_macro_grammar

    @property
    def parse_string_grammar(self) -> ppa.ParserElement:
        if self._parse_string_grammar is None:
            self._parse_string_grammar = ppa.OneOrMore(self.grammar.copy())
        return self._parse_string_grammar

    @property
    def parse_string_grammar(self) -> ppa.ParserElement:
        if self._parse_string_grammar is None:
            self._parse_string_grammar = ppa.OneOrMore(self.grammar.copy())
        return self._parse_string_grammar

    @property
    def parse_string_non_macro_grammar(self) -> ppa.ParserElement:
        if self._parse_string_non_macro_grammar is None:
            self._parse_string_non_macro_grammar = ppa.OneOrMore(self.non_macro_grammar.copy())
        return self._parse_string_non_macro_grammar

    def ensure_all_grammars(self) -> None:
        _ = self.grammar
        _ = self.parse_string_grammar

        _ = self.non_macro_grammar
        _ = self.parse_string_non_macro_grammar

    def scan_string(self,
                    instring: str,
                    max_matches: int = ppa.core._MAX_INT,
                    overlap: bool = False,
                    *,
                    debug: bool = False,
                    maxMatches: int = ppa.core._MAX_INT,
                    allow_macro_values: bool = True) -> Generator[tuple[ppa.ParseResults, int, int], None, None]:

        grammar = self.grammar if allow_macro_values is True else self.non_macro_grammar
        return grammar.scan_string(instring=instring, max_matches=max_matches, overlap=overlap, debug=debug, maxMatches=maxMatches)

    def parse_string(self,
                     instring: str,
                     parse_all: bool = False,
                     *,
                     parseAll: bool = False,
                     debug: bool = False,
                     allow_macro_values: bool = True) -> ConfigParsingResult:

        grammar = (self.parse_string_grammar if allow_macro_values is True else self.parse_string_non_macro_grammar).copy().set_debug(debug)

        return ConfigParsingResult.from_parser_result(grammar.parse_string(instring=instring, parse_all=parse_all, parseAll=parseAll))

    def parse_file(self,
                   file_or_filename: Union[str, Path, TextIO],
                   encoding: str = "utf-8",
                   parse_all: bool = False,
                   *,
                   parseAll: bool = False,
                   debug: bool = False,
                   allow_macro_values: bool = True) -> ppa.ParseResults:

        grammar = (self.parse_string_grammar if allow_macro_values is True else self.parse_string_non_macro_grammar).copy().set_debug(debug)

        return ConfigParsingResult.from_parser_result(grammar.parse_file(file_or_filename=file_or_filename, encoding=encoding, parse_all=parse_all, parseAll=parseAll))


CONFIG_GRAMMAR = _ConfigGrammar()


def find_sub_cfg(in_text: str, sub_cfg_name: str) -> str:
    class_start_regex = re.compile(rf"^\s*class {sub_cfg_name}[\s\n]*(?=\{'{'})", re.MULTILINE)
    m = class_start_regex.search(in_text)

    pos = m.start()
    pre_mod_text = in_text[pos:]
    cfg_text = []
    opened_braces = 0
    in_quotes = False

    for char in pre_mod_text:

        cfg_text.append(char)

        if char == '"':
            in_quotes = not in_quotes

        elif char == "{":
            if in_quotes is False:
                opened_braces += 1

        elif char == "}":
            if in_quotes is False:
                opened_braces -= 1

        elif char == ";":
            if in_quotes is False and opened_braces == 0:
                break

    new_text = ''.join(cfg_text)
    return new_text


def do(in_file: Path):
    sep = "+-" * 50

    s = "-"
    e = "-"

    print("getting grammar", flush=True)

    collected_classes = []

    # grammar.enable_left_recursion(1024, force=True)
    pool = ThreadPoolExecutor()

    print("starting parsing\n\n", flush=True)
    text = pre_clean(in_file.read_text(encoding='utf-8', errors='ignore')).strip()

    for tt in CONFIG_GRAMMAR.scan_string(text):
        # for tt in CONFIG_GRAMMAR.parse_string(text, parse_all=True):

        _c, s, e = (tt[0], tt[1], tt[2])
        print(f"{_c=}")
        c = _c[0]
        if isinstance(c, ClassToken):
            print(f"\ncreated class {c.name!r}", flush=True)
            pool.submit(write_to_json, c)
        elif isinstance(c, BaseAttributeToken):
            print(f"\ncreated ATTRIBUTE {c.name}\n")
    pool.shutdown(wait=True)


def do_other(in_file: Path):
    text = pre_clean(in_file.read_text(encoding='utf-8', errors='ignore')).strip()
    result = CONFIG_GRAMMAR.parse_string(instring=text, parse_all=True)
    print(f"{result.tokens=}")
    print(f"{len(result.all_tokens)=}")
    print(f"{len(set(result.all_tokens))=}")
    for t in result.all_tokens:
        if t.container_path == "Mission.Connections.Links.Item38.CustomData":
            pprint(t.all_attributes[0].get_parents())


def do_graph(in_file: Path):

    import networkx as nx
    import matplotlib.pyplot as plt

    graph = nx.DiGraph()
    edges = []
    labels = {}
    weights = {}
    added_children = 0

    def _add_children(in_item: ClassToken):
        nonlocal added_children
        if added_children >= 100:
            return
        print(f"adding children for {in_item!r}", flush=True)
        # for attr_child in in_item.all_attributes:
        #     graph.add_node(attr_child.container_path, shape="note")
        #     weights[(in_item.container_path, attr_child.container_path)] = len(attr_child.container_path.split("."))
        #     if attr_child.name == "name":
        #         labels[attr_child.container_path] = f"{attr_child.name}: {attr_child.value!r}"
        #     edges.append((in_item.container_path, attr_child.container_path))

        for class_child in in_item.all_classes:
            graph.add_node(class_child.container_path, shape="house")
            node_label = f"{class_child.name}: {class_child.parent_name}" if class_child.parent_name else class_child.name
            labels[class_child.container_path] = node_label
            weights[(in_item.container_path, class_child.container_path)] = int(len(class_child.container_path.split(".")) * 1.25)
            edges.append((in_item.container_path, class_child.container_path))
            added_children += 1
            if len(class_child.container_path.split(".")) <= 5:
                _add_children(class_child)

    text = pre_clean(in_file.read_text(encoding='utf-8', errors='ignore')).strip()
    text = find_sub_cfg(text, "CfgWeapons")
    CONFIG_GRAMMAR.set_debug(True)
    result = CONFIG_GRAMMAR.parse_string(text, parse_all=True)

    print("-" * 100)
    pprint(result.tokens)

    print("-" * 100)

    # base_item = result["Mission"]
    base_item = result["CfgWeapons"]
    print(f"{len(base_item.all_attributes)+len(base_item.all_classes)=}")
    graph.add_node(base_item.container_path, width="1.5", height="1.0")
    labels[base_item.container_path] = base_item.name
    _add_children(base_item)
    graph.add_edges_from(edges, headport="n")

    print("setting node and edge attributes", flush=True)
    # nx.set_node_attributes(graph, {k: f"{v[0]},{v[1]}" for k, v in nx.kamada_kawai_layout(graph).items()}, "pos")
    nx.set_node_attributes(graph, labels, "label")
    nx.set_edge_attributes(graph, weights, "weight")

    # nx.set_node_attributes(graph, nx.planar_layout(graph), "pos")
    print("converting to agraph", flush=True)
    a_graph = nx.nx_agraph.to_agraph(graph)

    print("setting graph attributes", flush=True)
    a_graph.graph_attr["splines"] = "false"
    a_graph.graph_attr["overlap"] = "false"
    a_graph.graph_attr["ranksep"] = "2.5"
    a_graph.graph_attr["center"] = "true"
    a_graph.graph_attr["nodesep"] = "0.50"

    print("setting layout", flush=True)
    a_graph._layout("dot")
    print("drawing to file", flush=True)
    a_graph.draw("file.png")
    a_graph.write("file.dot")

    # subax1 = plt.subplot(121)
    # nx.draw(graph, nx.kamada_kawai_layout(graph), node_shape="d", labels=labels)
    # plt.show()


def get_all_parent_names(in_item: ClassToken, in_base_item: ClassToken):

    def _iter_parent_names(_item: ClassToken) -> Generator[str, None, None]:
        if _item.parent_name is not None:
            parent_item = getattr(in_base_item, _item.parent_name, None)
            if parent_item is not None:
                yield parent_item.name
                yield from _iter_parent_names(parent_item)
            else:
                print(f"unable to locate class_token with name {_item.parent_name}")

    return tuple(_iter_parent_names(in_item))


def do_arma_cfg_graph(in_file: Path):

    import networkx as nx

    graph = nx.DiGraph()
    edges = []
    labels = {}
    weights = {}
    added_children = 0
    _all_names = []

    def _add_children(in_item: ClassToken, in_base_item: ClassToken, base_class: str = None):
        nonlocal added_children
        # if added_children >= 100:
        #     return
        base_class = base_class if base_class is not None else "Default"
        if in_item.name.startswith("tf_") or "_TFAR_" in in_item.name or in_item.name.startswith("ACE_dogtag_"):
            return

        all_parent_names = get_all_parent_names(in_item=in_item, in_base_item=in_base_item)
        try:
            top_parent = all_parent_names[-1]
        except IndexError:
            top_parent = ""
        if base_class is not None:
            if in_item.name != base_class and base_class not in all_parent_names:
                return
        try:
            display_name = in_item.displayName
        except (KeyError, AttributeError):
            display_name = ""
        kwargs = {}
        kwargs["fontsize"] = "50.0" if in_item.name != base_class else "75.0"
        try:
            kwargs["group"] = all_parent_names[0]
        except IndexError:
            pass
        kwargs["fillcolor"] = "darkseagreen1"
        if display_name == "":
            kwargs["fillcolor"] = "thistle1"
        if in_item.name == base_class:
            kwargs["fillcolor"] = "yellow"

        graph.add_node(in_item.name, shape="record", style="filled", ** kwargs)
        node_label = f"{in_item.name}| {display_name}"
        labels[in_item.name] = node_label

        if in_item.name != base_class:
            edges.append((in_item.parent_name, in_item.name))
            weights[(in_item.parent_name, in_item.name)] = (len(all_parent_names) * 2) if display_name != "" else (len(all_parent_names) // 2)
            identifier = f"{in_item.name}: {in_item.parent_name}"
            _all_names.append(f"{identifier:<100} -> {all_parent_names!r}")
        else:
            _all_names.append(f"{in_item.name}")

        added_children += 1

    text = pre_clean(in_file.read_text(encoding='utf-8', errors='ignore')).strip()
    text = find_sub_cfg(text, "CfgWeapons")

    result = CONFIG_GRAMMAR.parse_string(text, parse_all=True)

    # base_item = result["Mission"]
    base_item = result["CfgWeapons"]
    print("-" * 100)
    print(f"{len(base_item.all_classes)=}")

    print("-" * 100)

    # graph.add_node("CfgWeapons", width="1.5", height="1.0")
    # labels["CfgWeapons"] = base_item.name
    for child in base_item.all_classes:
        _add_children(child, in_base_item=base_item, base_class="CUP_arifle_AK_Base")
    with THIS_FILE_DIR.joinpath("all_names.txt").open("w", encoding='utf-8', errors='ignore') as f:
        for name in sorted(set(_all_names), key=lambda x: (":" in x, x.split(":")[-1].split("->")[0].strip().casefold())):
            f.write(f"{name.split('->')[0].strip().split(':')[0].strip()}\n")
    graph.add_edges_from(edges, headport="w", tailport="e")

    print("setting node and edge attributes", flush=True)
    # nx.set_node_attributes(graph, {k: f"{v[0]},{v[1]}" for k, v in nx.kamada_kawai_layout(graph).items()}, "pos")
    nx.set_node_attributes(graph, labels, "label")
    nx.set_edge_attributes(graph, weights, "weight")

    # nx.set_node_attributes(graph, nx.planar_layout(graph), "pos")
    print("converting to agraph", flush=True)
    a_graph = nx.nx_agraph.to_agraph(graph)
    print("setting graph attributes", flush=True)
    a_graph.graph_attr["splines"] = "false"
    a_graph.graph_attr["overlap"] = "false"
    a_graph.graph_attr["ranksep"] = "5.0 equally"
    a_graph.graph_attr["center"] = "true"
    a_graph.graph_attr["nodesep"] = "2.5"
    a_graph.graph_attr["rankdir"] = "LR"
    a_graph.graph_attr["newrank"] = "true"
    a_graph.graph_attr["searchsize"] = "100000"
    a_graph.graph_attr["nslimit"] = "10000.0"
    a_graph.graph_attr["nslimit1"] = "10000.0"
    a_graph.graph_attr["bgcolor"] = "transparent"
    # a_graph.graph_attr["mclimit"] = "10.0"

    a_graph.graph_attr["ordering"] = "in"
    a_graph.graph_attr["packMode"] = "graph"
    a_graph.graph_attr["concentrate"] = "true"
    a_graph.graph_attr["TBbalance"] = "min"
    # a_graph.graph_attr["fontsize"] = "100.0"

    print("setting layout", flush=True)
    a_graph = a_graph.tred().unflatten()
    a_graph.layout("dot")
    print("drawing to file", flush=True)

    a_graph.draw("file.pdf", format="pdf")
    a_graph.draw("file.svg", format="svg")
    a_graph.draw("file.png", format="png")

    a_graph.write("file.dot")

    # subax1 = plt.subplot(121)
    # nx.draw(graph, nx.kamada_kawai_layout(graph), node_shape="d", labels=labels)
    # plt.show()


def parse_with_macros(in_file: Path):
    _ = CONFIG_GRAMMAR.parse_file(in_file, parse_all=True, allow_macro_values=True)


def parse_without_macros(in_file: Path):
    _ = CONFIG_GRAMMAR.parse_file(in_file, parse_all=True, allow_macro_values=False)


EXTENSIONS = {".paa", ".p3d", ".rtm", ".wrp", ".rvmat"}


def visit(in_token: Union[ClassToken, BaseAttributeToken]):

    def visit_attribute(in_attribute: BaseAttributeToken):

        if isinstance(in_attribute.value, str) and any(in_attribute.value.endswith(i) for i in EXTENSIONS):
            yield in_attribute.value.split("/")[-1]

    def visit_class(in_class: ClassToken):
        yield in_class.name
        for attr in in_class.all_attributes:
            yield from visit(attr)

        for kls in in_class.all_classes:
            yield from visit(kls)

    if isinstance(in_token, ClassToken):
        yield from visit_class(in_token)

    elif isinstance(in_token, BaseAttributeToken):
        yield from visit_attribute(in_token)

    else:
        raise RuntimeError(f"weird token {in_token} ({type(in_token)})")


def get_all_cfg_class_names(in_text: str) -> Generator[str, None, None]:
    pattern = re.compile(rf"^\s*class (?P<name>Cfg\w+)[\s\n]*(?=\{'{'})", re.MULTILINE)
    found_names = set()
    for m in pattern.finditer(in_text):
        name = m.group("name")
        if name not in found_names:
            found_names.add(name)
            yield name


def just_parse(in_file: Path):

    CONFIG_GRAMMAR.ensure_all_grammars()
    CONFIG_GRAMMAR.parse_string_non_macro_grammar.disable_memoization()
    CONFIG_GRAMMAR.parse_string_grammar.disable_memoization()
    output_folder = THIS_FILE_DIR.joinpath("output").resolve()
    output_folder.mkdir(parents=True, exist_ok=True)
    text = pre_clean(in_file.read_text(encoding='utf-8', errors='ignore')).strip()

    def _get_chunks(in_text: str):

        all_sub_cfg_names = ["CfgWeapons",
                             "CfgVehicles",
                             "CfgMagazines",
                             "CfgMagazineWells",
                             "CfgIdentities",
                             "CfgGlasses",
                             "CfgAmmo"]

        random.shuffle(all_sub_cfg_names)
        random.shuffle(all_sub_cfg_names)
        random.shuffle(all_sub_cfg_names)

        for sub_cfg_name in all_sub_cfg_names:
            print(f"yielding {sub_cfg_name!r}", flush=True)
            yield (sub_cfg_name, find_sub_cfg(in_text, sub_cfg_name))
            sleep(0.25)
        print("finished getting all sub_cfg_texts", flush=True)

    def _handle_sub_cfg(in_sub_cfg_name_and_in_text: tuple[str, str]):
        sub_text = in_sub_cfg_name_and_in_text[1]
        in_sub_cfg_name = in_sub_cfg_name_and_in_text[0]
        if sub_text is None:
            return None, None
        result = CONFIG_GRAMMAR.parse_string(sub_text, parse_all=True, allow_macro_values=False)
        token = None
        name = None
        with output_folder.joinpath(f"{in_sub_cfg_name}.json").open("w", encoding='utf-8', errors='ignore') as f:
            for name, token in result.tokens.items():
                all_classes = list(token.all_classes)
                for sub_t in token.all_classes:
                    sub_t.find_parent(all_classes)

                json.dump(token.to_json(), f, indent=4, default=str)
        return name, token

    with output_folder.joinpath("all_names.txt").open("w", encoding='utf-8', errors='ignore') as f:
        with ThreadPoolExecutor(3) as pool:
            for t_name, t in pool.map(_handle_sub_cfg, _get_chunks(text)):
                if t is None:
                    print(f"!!!!!!!!!!!! t is None for {t_name!r}", flush=True)
                    continue
                print(f"{t_name=}", flush=True)
                for c_t in t.all_classes:
                    resolved_parent_name = c_t.parent.parent.name if c_t.parent is not None and c_t.parent.parent is not None else None
                    f.write(f"{t_name:<20} -> {c_t.name:^50} -> {c_t.parent_name} ({resolved_parent_name})\n")

                f.write("\n\n" + ("-" * 100) + "\n\n")
                f.flush()

# region [Main_Exec]


if __name__ == '__main__':
    # the_file_path = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Arma 3\AiO.1.10.149954.cpp")

    # CONFIG_GRAMMAR.ensure_all_grammars()
    # # just_parse(the_file_path)
    # do_arma_cfg_graph(the_file_path)
    just_parse(Path(r"D:\Dropbox\hobby\Modding\Programs\Github\My_Repos\Antistasi_SQF_tools\antistasi_sqf_tools\parsing\config_parsing\AiO.1.10.149954.cpp").resolve())
# endregion [Main_Exec]
