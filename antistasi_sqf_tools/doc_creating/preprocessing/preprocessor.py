"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import importlib
from types import ModuleType
from typing import TYPE_CHECKING
from pathlib import Path

# * Local Imports --------------------------------------------------------------------------------------->
from antistasi_sqf_tools.utilities import push_cwd

# * Type-Checking Imports --------------------------------------------------------------------------------->
if TYPE_CHECKING:
    from antistasi_sqf_tools.doc_creating.config_handling import DocCreationConfig

# endregion [Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion [Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion [Constants]


def preprocessing_noop(preprocessor: "PreProcessor"):
    ...


class PreProcessor:

    def __init__(self,
                 source_dir: Path,
                 target_dir: Path,
                 preprocessing_conf_file: Path,
                 doc_creation_config: "DocCreationConfig") -> None:
        self.source_dir = source_dir
        self.target_dir = target_dir
        self.preprocessing_conf_file = preprocessing_conf_file
        self.doc_creation_config = doc_creation_config
        self._preprocessing_module: ModuleType = None

    def _load_preprocessing_file(self) -> ModuleType:
        spec = importlib.util.spec_from_file_location("preprocessing_conf", self.preprocessing_conf_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self._preprocessing_module = module

    def _load_preprocessor_options(self):
        ...

    def pre_process(self) -> None:
        with push_cwd(self.source_dir):
            self._load_preprocessing_file()
            self._load_preprocessor_options()
            getattr(self._preprocessing_module, "before_preprocess", preprocessing_noop)(self)
            getattr(self._preprocessing_module, "preprocess", preprocessing_noop)(self)
            getattr(self._preprocessing_module, "after_preprocess", preprocessing_noop)(self)

# region [Main_Exec]


if __name__ == '__main__':
    pass

# endregion [Main_Exec]
