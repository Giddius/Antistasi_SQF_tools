"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import re
import inspect
from enum import Enum, auto
from string import punctuation, ascii_lowercase
from typing import Any, Union, Literal, Mapping, Callable, Iterable, Optional
from pathlib import Path
from textwrap import dedent

# * Third Party Imports --------------------------------------------------------------------------------->
import pyparsing as ppa

# endregion [Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]

# endregion [Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()


# endregion [Constants]
class BaseGidEnum(Enum):
    @classmethod
    def _missing_(cls, value: object) -> Any:
        if isinstance(value, str):
            mod_value = value.casefold()
            for member_name, member_value in cls.__members__.items():
                if member_name.casefold() == mod_value or member_value == mod_value:
                    return cls(member_value)
                if isinstance(member_value, str) and member_value.casefold() == mod_value:
                    return cls(member_value)
        return super()._missing_(value)

    @classmethod
    def is_in_value(cls, other: Any) -> bool:
        return other in {member.value for name, member in cls.__members__.items()}

    def __str__(self) -> str:
        return self.name


class StringCase(BaseGidEnum):
    """
    _summary_

    - SNAKE: 'example_variable_name'
    - SCREAMING_SNAKE: 'EXAMPLE_VARIABLE_NAME'
    - CAMEL: 'exampleVariableName'
    - PASCAL: 'ExampleVariableName'
    - KEBAP: 'example-variable-name'
    - SPLIT: 'example variable name'
    - TITLE: 'Example Variable Name'
    - UPPER: 'EXAMPLE VARIABLE NAME'
    - BLOCK_UPPER: 'EXAMPLEVARIABLENAME'

    - CLASS: see `PASCAL`

    Args:
        BaseGidEnum (_type_): _description_
    """
    SNAKE = auto()
    SCREAMING_SNAKE = auto()
    CAMEL = auto()
    PASCAL = auto()
    KEBAP = auto()
    SPLIT = auto()
    TITLE = auto()
    UPPER = auto()
    BLOCK_UPPER = auto()
    # aliases
    CLASS = PASCAL


STRING_CASE_FUNC_TYPE = Callable[[Iterable[str]], str]


# TODO: Rewrite as normal class/Module-Singleton
class _StringCaseConverter:
    """ """
    SNAKE = StringCase.SNAKE
    SCREAMING_SNAKE = StringCase.SCREAMING_SNAKE
    CAMEL = StringCase.CAMEL
    PASCAL = StringCase.PASCAL
    KEBAP = StringCase.KEBAP
    SPLIT = StringCase.SPLIT
    CLASS = StringCase.CLASS
    TITLE = StringCase.TITLE
    BLOCK_UPPER = StringCase.BLOCK_UPPER

    split_pascal_case_regex = re.compile(r"(?<!\_)(\B[A-Z])")
    snake_case_to_pascal_case_regex = re.compile(r"(_|^)(\w)")
    _word_list_split_chars = {'-', '_', ' '}

    __slots__ = ("_split_grammar", "_word_list_split_regex", "_dispatch_table", "_bad_chars")

    def __init__(self) -> None:
        self._split_grammar: Optional[ppa.ParserElement] = None

        self._word_list_split_regex = None

        self._dispatch_table: Optional[dict[str, STRING_CASE_FUNC_TYPE]] = None
        self._bad_chars: Optional[set[str]] = None

    @property
    def bad_chars(self) -> set[str]:
        if self._bad_chars is None:
            self._bad_chars = {c for c in punctuation if c not in self._word_list_split_chars}
        return self._bad_chars

    @property
    def word_list_split_regex(self) -> re.Pattern:
        if self._word_list_split_regex is None:
            self._word_list_split_regex = re.compile(r'|'.join(list(self._word_list_split_chars) + [r"(?=[A-Z])"]))
        return self._word_list_split_regex

    @property
    def dispatch_table(self) -> dict[StringCase, STRING_CASE_FUNC_TYPE]:
        if self._dispatch_table is None:
            self._dispatch_table = {}
            for meth_name, meth_obj in inspect.getmembers(self):
                if meth_name.startswith('_to_') and meth_name.endswith('_case'):
                    key_name = meth_name.removeprefix('_to_').removesuffix('_case')
                    self._dispatch_table[StringCase(key_name)] = meth_obj
        return self._dispatch_table

    @property
    def split_grammar(self) -> ppa.ParserElement:
        if self._split_grammar is None:
            underscore = ppa.Literal('_').suppress()
            dash = ppa.Literal("-").suppress()
            all_upper_word = ppa.Regex(r"[A-Z]+(?![a-z])")
            all_lower_word = ppa.Word(ascii_lowercase, ascii_lowercase)
            title_word = ppa.Regex(r"[A-Z][a-z]+")
            number = ppa.Word(ppa.nums)
            words = (title_word | all_upper_word | all_lower_word | number).set_parse_action(lambda x: x[0].casefold())
            grammar = words | underscore | dash
            self._split_grammar = ppa.OneOrMore(grammar)
        return self._split_grammar

    def _to_word_list(self, in_string: str) -> list[str]:
        """
        :param in_string: str:
        """
        parts: ppa.ParseResults = self.split_grammar.parse_string(in_string, parse_all=True)

        return [word for word in parts if word]

    @staticmethod
    def _to_block_upper_case(word_list: Iterable[str]) -> str:
        """
        :param word_list: Iterable[str]:
        """
        return ''.join(word.upper() for word in word_list)

    @staticmethod
    def _to_snake_case(word_list: Iterable[str]) -> str:
        """
        :param word_list: Iterable[str]:
        """
        return '_'.join(word_list).casefold()

    @staticmethod
    def _to_camel_case(word_list: Iterable[str]) -> str:
        """
        :param word_list: Iterable[str]:
        """
        return word_list[0].casefold() + ''.join(item.title() for item in word_list[1:])

    @staticmethod
    def _to_pascal_case(word_list: Iterable[str]) -> str:
        """
        :param word_list: Iterable[str]:
        """
        return ''.join(item.title() for item in word_list)

    @staticmethod
    def _to_kebap_case(word_list: Iterable[str]) -> str:
        """

        :param word_list: Iterable[str]:

        """
        return '-'.join(word_list)

    @staticmethod
    def _to_screaming_snake_case(word_list: Iterable[str]) -> str:
        """

        :param word_list: Iterable[str]:

        """
        return '_'.join(word_list).upper()

    @staticmethod
    def _to_split_case(word_list: Iterable[str]) -> str:
        """

        :param word_list: Iterable[str]:

        """
        return ' '.join(word_list)

    @staticmethod
    def _to_title_case(word_list: Iterable[str]) -> str:
        """

        :param word_list: Iterable[str]:

        """
        return ' '.join(word.title() for word in word_list)

    @staticmethod
    def _to_upper_case(word_list: Iterable[str]) -> str:
        """

        :param word_list: Iterable[str]:

        """
        return ' '.join(word.upper() for word in word_list)

    def remove_bad_chars(self, in_string: str) -> str:
        new_string = str(in_string)
        for char in self.bad_chars:
            new_string: str = new_string.replace(char, "")

        return new_string

    def convert_to(self, in_string: str, target_case: Union[str, StringCase], clean_in_string: bool = False) -> str:
        """

        :param in_string: str:
        :param target_case: Union[str, StringCase]:

        """
        if clean_in_string is True:
            in_string = self.remove_bad_chars(in_string)
        target_case = StringCase(target_case) if isinstance(target_case, str) else target_case
        word_list = self._to_word_list(in_string)
        return self.dispatch_table.get(target_case)(word_list)


StringCaseConverter = _StringCaseConverter()


def replace_by_dict(in_string: str, in_dict: dict[str, str]) -> str:
    """

    :param in_string: str:
    :param in_dict: dict[str, str]:

    """
    mod_string = in_string
    for key, value in in_dict.items():
        mod_string = mod_string.replace(key, value)
    return mod_string


def extract_by_map(in_string: str, extract_data: Union[Iterable[str], Mapping[str, str]]) -> Iterable[str]:
    """

    :param in_string: str:
    :param extract_data: Union[Iterable[str], Mapping[str, str]]:

    """
    parts = []
    re_pattern = re.compile(r'|'.join(extract_data))
    for match in re_pattern.finditer(in_string):
        matched_str = match.group()
        parts.append(matched_str)
    if isinstance(extract_data, Mapping):
        return [extract_data.get(part) for part in parts]
    return parts


SPACE_CLEANING_REGEX = re.compile(r" +")
NEWLINE_CLEANING_REGEX = re.compile(r"\n+")


def clean_whitespace(in_text: str, replace_newline: bool = False) -> str:
    """

    :param in_text: str:
    :param replace_newline: bool:  (Default value = False)

    """
    cleaned_text = SPACE_CLEANING_REGEX.sub(' ', in_text)
    if replace_newline is True:
        cleaned_text = NEWLINE_CLEANING_REGEX.sub(' ', cleaned_text)
    return cleaned_text


def shorten_string(in_text: str, max_length: int, shorten_side: Literal["right", "left"] = "right", placeholder: str = '...', clean_before: bool = True, ensure_space_around_placeholder: bool = False, split_on: str = r'\s|\n') -> str:
    """

    :param in_text: str:
    :param max_length: int:
    :param shorten_side: Literal["right", "left"]:  (Default value = "right")
    :param placeholder: str:  (Default value = "...")
    :param clean_before: bool:  (Default value = True)
    :param ensure_space_around_placeholder: bool:  (Default value = False)
    :param split_on: str:

    """
    max_length = int(max_length)
    if shorten_side.casefold() not in {"left", "right"}:
        raise ValueError(shorten_side)

    if clean_before is True:
        in_text = clean_whitespace(in_text, replace_newline=False)

    if len(in_text) <= max_length:
        return in_text

    if ensure_space_around_placeholder is True:
        placeholder = f" {placeholder.strip()}" if shorten_side == "right" else f"{placeholder.strip()} "

    max_length = max_length - len(placeholder)

    new_text = in_text[:max_length] if shorten_side == 'right' else in_text[-max_length:]
    if split_on == "any":
        split_on = r"."
    find_regex = re.compile(split_on)
    last_space_position = list(find_regex.finditer(new_text))

    return new_text[:last_space_position[-1].span()[0]].strip() + placeholder if shorten_side == 'right' else placeholder + new_text[last_space_position[0].span()[0]:].strip()


def split_quotes_aware(text: str, split_chars: Iterable[str] = None, quote_chars: Iterable[str] = None, strip_parts: bool = True) -> list[str]:
    """Splits a string on but not if the separator char is inside of quotes.

    :param text: The string to split.
    :type text: str
    :param split_chars: The characters to split on. Defaults to `,`.
    :type split_chars: Iterable[str]
    :param quote_chars: The quote chars that should be considered real quotes. Defaults to `"` and `'`.
    :type quote_chars: Iterable[str]
    :param strip_parts: If each found substrin should be striped of preceding and trailing whitespace in the result. Defaults to True.
    :type strip_parts: bool
    :param text: str:
    :param split_chars: Iterable[str]:  (Default value = None)
    :param quote_chars: Iterable[str]:  (Default value = None)
    :param strip_parts: bool:  (Default value = True)
    :returns: The found sub-parts.
    :rtype: list[str]

    """
    split_chars = {','} if split_chars is None else set(split_chars)
    quote_chars = {"'", '"'} if quote_chars is None else set(quote_chars)
    parts = []
    temp_chars = []
    inside_quotes: str = None

    def _add_part():
        """ """
        nonlocal parts
        nonlocal temp_chars
        part = ''.join(temp_chars)
        if strip_parts is True:
            part = part.strip()
        for quote_char in quote_chars:
            if part.startswith(quote_char) and part.endswith(quote_char):
                part = part.strip(quote_char)
        if part:
            parts.append(part)
        temp_chars.clear()

    for char in text:
        if char in split_chars and inside_quotes is None:
            _add_part()
        else:
            temp_chars.append(char)

            if char in quote_chars and inside_quotes is None:
                inside_quotes = char
            elif char in quote_chars and inside_quotes == char:
                inside_quotes = None

    if temp_chars:
        _add_part()

    return parts


def make_attribute_name(in_string: str) -> str:
    """

    :param in_string: str:

    """

    # Remove invalid characters
    in_string = re.sub(r'-', '_', in_string)
    in_string = re.sub('[^0-9a-zA-Z_]', '', in_string)

    # Remove leading characters until we find a letter or underscore
    in_string = re.sub('^[^a-zA-Z_]+', '', in_string)

    return in_string.casefold()


def fix_multiple_quotes(_text: str, max_consecutive_quotes: int = None) -> str:
    """

    :param _text: str:
    :param max_consecutive_quotes: int:  (Default value = None)

    """

    def _replace_function(match: re.Match):
        """

        :param match: re.Match:

        """
        return match.group()[0]
    if max_consecutive_quotes is None:
        pattern = r"""(\"+)|(\'+)"""
    elif max_consecutive_quotes <= 1:
        raise ValueError("'max_consecutive_quotes' cannot be less than 2.")
    else:
        pattern = rf"""(\"{{2,{max_consecutive_quotes}}})|(\'{{2,{max_consecutive_quotes}}})"""
    return re.sub(pattern, _replace_function, _text)


def escape_doubled_quotes(text: str) -> str:
    """

    :param text: str:

    """
    def _replace_function(match: re.Match):
        """

        :param match: re.Match:

        """
        return r"\ ".strip() + match.group()[0]

    return re.sub(r"""(\"{2})|(\'{2})""", _replace_function, text)


def deindent(in_text: str, ignore_first_line: bool = False) -> str:
    """

    :param in_text: str:
    :param ignore_first_line: bool:  (Default value = False)

    """
    if in_text == "":
        return in_text
    pre_whitespace_regex = re.compile(r"\s*")
    lines = in_text.splitlines()
    white_space_levels = []
    if ignore_first_line is True:
        _first_line = lines.pop(0)
    for line in lines:
        if not line:
            continue
        if match := pre_whitespace_regex.match(line):
            ws = match.group()
            if len(ws) == len(line):
                continue
            white_space_levels.append(len(match.group()))
        else:

            white_space_levels.append(0)

    try:
        min_ws_level = min(white_space_levels) if len(white_space_levels) > 1 else white_space_levels[0]
    except IndexError:
        min_ws_level = 0
    combined = '\n'.join(line[min_ws_level:] for line in lines)
    if ignore_first_line is True:
        combined = '\n' + combined if combined else ""
        combined = _first_line + combined
    return combined


def multi_line_dedent(in_text: str, strip_pre_lines: bool = True, strip_post_lines: bool = True) -> str:
    """

    :param in_text: str:
    :param strip_pre_lines: bool:  (Default value = True)
    :param strip_post_lines: bool:  (Default value = True)

    """
    text = dedent(in_text)

    if strip_pre_lines is True:
        lines = text.splitlines()
        while lines[0] == "":
            lines.pop(0)
        text = '\n'.join(lines)
    if strip_post_lines is True:
        text = text.rstrip()
    return text


def strip_only_wrapping_empty_lines(in_text: str) -> str:
    """

    :param in_text: str:

    """
    empty_line_pattern = re.compile(r"(^\s*)|(\s*$)")
    return empty_line_pattern.sub("", in_text)


def string_strip(in_string: str, chars: str = None) -> str:
    """

    :param in_string: str:
    :param chars: str:  (Default value = None)

    """
    return in_string.strip(chars)


def remove_chars(in_string: str, *chars) -> str:
    """

    :param in_string: str:
    :param chars: Iterable[str]:

    """
    return ''.join(char for char in in_string if char not in set(chars))


def string_map_replace(in_string: str, replacement_map: Mapping[str, str]) -> str:
    new_string = str(in_string)
    for k, v in replacement_map.items():
        new_string = new_string.replace(k, v)

    return new_string


# region [Main_Exec]


if __name__ == '__main__':
    pass
# endregion [Main_Exec]
