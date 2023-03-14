
# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
from typing import TYPE_CHECKING
from pathlib import Path

# * Third Party Imports --------------------------------------------------------------------------------->
from sphinx.util.fileutil import copy_asset

# * Local Imports --------------------------------------------------------------------------------------->
from antistasi_sqf_tools import __version__

from .strike_role import strike_node, strike_role, html_visit_strike_node, html_depart_strike_node
from .cards_as_label import register_cards_as_label
from .caveat_admonition import Caveat, caveat, visit_caveat_node, depart_caveat_node


# * Type-Checking Imports --------------------------------------------------------------------------------->
if TYPE_CHECKING:
    from sphinx.application import Sphinx as SphinxApplication

# endregion [Imports]


THIS_FILE_DIR = Path(__file__).parent.absolute()

STYLE_SHEET_FILE = THIS_FILE_DIR.joinpath("misc_additions_style.css").resolve()


def add_style_sheet(app: "SphinxApplication", exc: Exception) -> None:

    if exc is None and app.builder.format == 'html':
        src = STYLE_SHEET_FILE
        dst = Path(app.outdir).joinpath('_static').resolve()
        copy_asset(str(src), str(dst))


def setup(app: "SphinxApplication") -> None:
    app.add_node(strike_node, html=(html_visit_strike_node, html_depart_strike_node))
    app.add_role('strike', strike_role)
    app.add_role('del', strike_role)

    app.add_node(caveat, html=(visit_caveat_node, depart_caveat_node))
    app.add_directive("caveat", Caveat, True)
    app.add_directive("cave", Caveat, True)

    app.add_config_value("cards_as_labels", False, "", types=[bool])
    app.connect('doctree-read', register_cards_as_label)

    app.connect('build-finished', add_style_sheet)

    app.add_css_file("misc_additions_style.css")
    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
