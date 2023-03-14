
# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import os
from typing import TYPE_CHECKING, TypeAlias
from pathlib import Path

# * Local Imports --------------------------------------------------------------------------------------->
from antistasi_sqf_tools import __version__

from .misc_additions import setup as misc_additions_setup
from .links_collection import setup as links_collection_setup

# * Type-Checking Imports --------------------------------------------------------------------------------->
if TYPE_CHECKING:
    from sphinx.config import Config as SphinxConfig
    from sphinx.application import Sphinx as SphinxApplication
    _SphinxApplication: TypeAlias = SphinxApplication
    _SphinxConfig: TypeAlias = SphinxConfig


# endregion [Imports]


def on_config_inited(app: "_SphinxApplication", config: "_SphinxConfig") -> None:
    """
    Adds the original source-path and original target-path to the sphinx-app.

    So those can be accessed even when building via `IsolatedBuildEnvironment`.

    :type app: SphinxApplication

    :type config: SphinxConfig
    """

    original_source_dir = os.getenv("ORIGINAL_DOC_SOURCE_DIR", None)
    if original_source_dir is not None:
        app.original_source_dir = Path(original_source_dir).resolve()

    original_target_dir = os.getenv("ORIGINAL_DOC_TARGET_DIR", None)
    if original_target_dir is not None:
        app.original_target_dir = Path(original_target_dir).resolve()


def setup(app: "SphinxApplication") -> None:
    app.connect("config-inited", on_config_inited, priority=1)
    links_collection_setup(app)
    misc_additions_setup(app)
    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
