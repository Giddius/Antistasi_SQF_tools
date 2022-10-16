"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import re
import json
import sys
from pathlib import Path
from textwrap import dedent, indent
from functools import reduce
from collections import defaultdict
import os
from operator import or_
# * Third Party Imports --------------------------------------------------------------------------------->
import pp
from gidapptools.general_helper.timing import get_dummy_profile_decorator_in_globals
from gidapptools.general_helper.string_helper import StringCase, StringCaseConverter
from pprint import pprint, pformat
import pyparsing as ppa
from pyparsing import common as ppc, unicode as ppu
# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]
get_dummy_profile_decorator_in_globals()
THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]

CHECK_FILE = Path(r"D:\Dropbox\hobby\Modding\Programs\Github\My_Repos\Antistasi_SQF_tools\antistasi_sqf_tools\parsing\code_parsing\sqf_parsing\header_handling\header_check_file.sqf").resolve()

OUT_FOLDER = THIS_FILE_DIR.joinpath("output")
OUT_FOLDER.mkdir(exist_ok=True, parents=True)

for file in OUT_FOLDER.iterdir():
    if file.is_file() is True:
        file.unlink(missing_ok=True)

header_regex = re.compile(r"\s*(/\*)(?P<header_text>.*?)(\*/)", re.DOTALL)


@profile
def get_header(in_file: Path) -> str:
    match = header_regex.match(in_file.read_text(encoding='utf-8', errors='ignore'))

    if match:
        return match.group("header_text").strip()


@profile
def make_grammar():
    # type grammar
    arrow_left = ppa.Suppress("<")
    arrow_right = ppa.Suppress(">")
    pipe_char = ppa.Suppress("|")
    all_types = ppa.Forward()

    def make_type_expression(in_name: str) -> ppa.ParseExpression:
        return arrow_left + ppa.Literal(in_name.upper()) + arrow_right

    string_typus = make_type_expression("STRING")
    object_typus = make_type_expression("OBJECT")
    scalar_typus = make_type_expression("SCALAR")
    integer_typus = make_type_expression("INTEGER")
    bool_typus = make_type_expression("BOOL") | make_type_expression("BOOLEAN")
    code_typus = make_type_expression("CODE")
    any_typus = make_type_expression("ANY")
    pos3d_typus = make_type_expression("POS3D") | make_type_expression("POS3DTYPE")
    array_any_typus = make_type_expression("ARRAY<ANY>")

    all_types <<= reduce(or_, [string_typus, object_typus, scalar_typus, integer_typus, bool_typus, code_typus, pos3d_typus, array_any_typus, any_typus])

    # all_section_names = ["Maintainer",
    #                      "Description",
    #                      "Arguments",
    #                      "Return Value",
    #                      "Scope",
    #                      "Environment",
    #                      "Public",
    #                      "Dependencies",
    #                      "Example"]
    all_section_name_expressions = []
    all_section_names = ppa.Forward()
    COLON = ppa.Suppress(":")
    COMMA = ppa.Suppress(",")

    def make_section_name_expression(in_section_name: str) -> ppa.ParseExpression:

        expression = ppa.AtLineStart(ppa.Keyword(in_section_name) + COLON)
        all_section_name_expressions.append(expression)

        return expression

    maintainer_section_name = make_section_name_expression("Maintainer") | make_section_name_expression("Author")
    description_section_name = make_section_name_expression("Description")
    arguments_section_name = make_section_name_expression("Arguments")
    return_value_section_name = make_section_name_expression("Return Value") | make_section_name_expression("Returns")
    scope_section_name = make_section_name_expression("Scope")
    environment_section_name = make_section_name_expression("Environment")
    public_section_name = make_section_name_expression("Public")
    dependencies_section_name = make_section_name_expression("Dependencies")
    example_section_name = make_section_name_expression("Example")
    license_section_name = make_section_name_expression("License")
    all_section_names <<= reduce(or_, all_section_name_expressions)

    # maintainer section
    maintainer_name = ppa.Combine(ppa.OneOrMore(ppa.Word(ppu.alphanums), stop_on=all_section_names), adjacent=False, join_string=" ")

    maintainer_section = maintainer_section_name + ppa.delimited_list(maintainer_name, delim=ppa.Literal(",") | ppa.Literal("&"))("maintainer")

    # description section
    description_content = ppa.OneOrMore(ppa.Word(ppa.printables), stop_on=all_section_names)
    description_section = description_section_name + ppa.original_text_for(ppa.IndentedBlock(description_content))("description")

    # Arguments section
    arguments_content = (all_types("argument_type") + ppa.original_text_for(ppa.OneOrMore(ppa.Word(ppa.printables), stop_on=all_types | all_section_names))("argument_description")).set_parse_action(lambda x: x.as_dict())
    arguments_section = arguments_section_name + ppa.Group(ppa.IndentedBlock(arguments_content), True)("arguments")

    # scope section
    possible_values = ["Server",
                       "Server&HC",
                       "Clients",
                       "Client",
                       "HC",
                       "Any",
                       "Local Arguments",
                       "Global Arguments",
                       "Local Effect",
                       "Global Effect",
                       "Local Effects",
                       "Global Effects"]
    scope_content = ppa.delimited_list(ppa.one_of(strs=possible_values, caseless=True, as_keyword=True), delim=",")
    scope_section = scope_section_name + scope_content("scope")

    # environment section
    environment_content = ppa.one_of(strs=["Scheduled", "Unscheduled", "Any"], caseless=True, as_keyword=True)
    environment_section = environment_section_name + environment_content("environment")

    # public section

    public_content = ppa.one_of(strs=["Yes", "No"], caseless=True, as_keyword=True)
    public_section = public_section_name + public_content("public")

    # example section

    example_content = ppa.OneOrMore(ppa.Word(ppu.printables), stop_on=all_section_names)
    example_section = example_section_name + ppa.original_text_for(ppa.IndentedBlock(example_content))("example")

    return maintainer_section ^ description_section ^ arguments_section ^ scope_section ^ environment_section ^ public_section ^ example_section


GRAMMAR = make_grammar()


@profile
def do_it(in_file: Path):
    in_file = Path(in_file).resolve()
    grammar = GRAMMAR

    header_text = get_header(in_file)
    base_out = {"raw_header_text": header_text}
    _out = {}
    if header_text is None:
        return
    for i in grammar.search_string(header_text):
        _out |= i.as_dict()
    if _out == {}:
        return
    _out = base_out | _out
    return _out
    # with OUT_FOLDER.joinpath(f"{in_file.stem}.json").open("w", encoding='utf-8', errors='ignore') as f:
    #     json.dump(_out, f, default=str, sort_keys=False, indent=4)


def _file_name_to_section_name(in_file: Path) -> str:
    prefixes_to_remove = ("fn_", "UPSMON_")
    chars_to_replace_with_space = (".", "-", "_")
    file_name = in_file.stem.strip()
    pretty_file_name = file_name
    for prefix in prefixes_to_remove:
        pretty_file_name = pretty_file_name.removeprefix(prefix)

    pretty_file_name = StringCaseConverter.convert_to(pretty_file_name, StringCase.TITLE)

    pretty_file_name = pretty_file_name.strip()
    return f"{pretty_file_name}\n{'^'*(len(pretty_file_name)+2)}"


BASE_URL = "https://github.com/official-antistasi-community/A3-Antistasi/"
BASE_FOLDER = Path(r"D:\Dropbox\hobby\Modding\Programs\Github\Foreign_Repos\A3-Antistasi\A3A\addons").parent


def header_data_to_rst(in_file: Path, in_header_data: dict[str, object]):
    text_lines = []
    text_lines.append(_file_name_to_section_name(in_file))
    url = BASE_URL + '/'.join(p for p in in_file.relative_to(BASE_FOLDER).parts)
    text_lines.append(f"`{file.name} <{url}>`_")
    raw_header_text = in_header_data.pop("raw_header_text")

    for k, v in in_header_data.items():
        if k == "arguments":
            try:
                part_text = f".. admonition:: {k!s}\n\n   #. " + '\n   #. '.join(f"**{i['argument_type'].strip()}** {i['argument_description']}" for i in v)
            except AttributeError:
                print(f"{k=}")
                print(f"{v=}")
                print("-----")
                continue
        elif k in {"scope", "maintainer"}:
            part_text = f":{k.title()!s}: " + ',\n   '.join(f"**{i}**" for i in v)

        elif k == "example":
            part_text = f":{k.title()!s}: \n   .. code:: guess\n\n      " + '\n      '.join(l for l in dedent(v).splitlines()) + '\n\n'

        elif k == "description":
            part_text = f".. admonition:: {k.title()!s}\n\n   " + '\n   '.join(l for l in dedent(v).splitlines())
        else:
            try:
                part_text = f":{k.title()!s}: " + '\n   '.join(l for l in v.splitlines())
            except AttributeError:
                print("splitlines error")
                print(f"{k=}")
                print(f"{v=}")
                print("-----")
                continue
        text_lines.append(part_text)

    # text_lines.append(".. code:: guess\n\n   " + "\n   ".join(l for l in dedent(raw_header_text).splitlines()))
    tmp = """.. card::
   :class-header: header-2-light
   :class-card: sd-card-2\n\n"""
    return tmp + indent('\n\n'.join(text_lines), "   ")


# region[Main_Exec]
if __name__ == '__main__':
    pass

# endregion[Main_Exec]
