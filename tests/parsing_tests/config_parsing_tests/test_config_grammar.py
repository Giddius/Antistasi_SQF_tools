# region [Imports]

import pytest
from pytest import param
from pytest_lazyfixture import lazy_fixture

from pathlib import Path
from tests.example_data.example_config_files import FILES as EXAMPLE_CONFIG_FILES
from antistasi_sqf_tools.parsing.config_parsing.config_grammar import CONFIG_GRAMMAR

# endregion [Imports]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion [Constants]

test_full_config_grammar_params = [
    param(EXAMPLE_CONFIG_FILES["simple_cfgfunctions_1.hpp"], {"amount_top_classes": 1, "tokens": {"CfgFunctions"}}, id="simple_CfgFunctions_1")
]


@pytest.mark.parametrize(["in_config_file", "result"], test_full_config_grammar_params)
def test_full_config_grammar(in_config_file: Path, result: dict):
    text = in_config_file.read_text(encoding='utf-8', errors='ignore')
    parsed_data = CONFIG_GRAMMAR.parse_string(text, parse_all=True)
    assert len(parsed_data.tokens) == result["amount_top_classes"]
    assert set(parsed_data.tokens) == result["tokens"]
