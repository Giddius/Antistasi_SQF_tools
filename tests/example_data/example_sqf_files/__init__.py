from pathlib import Path


EXAMPLE_FILES_DIR = Path(__file__).parent.absolute()


_easy_file_names = ["fn_blackout",
                    "fn_buildHQ",
                    "fn_getAdmin"]


_intermediate_file_names = ["RHS_AI_USAF_Marines_Temperate",
                            "fn_canGoUndercover",
                            "fn_goUndercover"]


_hard_file_names = ["fn_selectIntel"]


EASY_EXAMPLES: dict[str, Path] = {file_name: EXAMPLE_FILES_DIR.joinpath(file_name + '.sqf').resolve() for file_name in _easy_file_names}


INTERMEDIATE_EXAMPLES: dict[str, Path] = {file_name: EXAMPLE_FILES_DIR.joinpath(file_name + '.sqf').resolve() for file_name in _intermediate_file_names}


HARD_EXAMPLES: dict[str, Path] = {file_name: EXAMPLE_FILES_DIR.joinpath(file_name + '.sqf').resolve() for file_name in _hard_file_names}
