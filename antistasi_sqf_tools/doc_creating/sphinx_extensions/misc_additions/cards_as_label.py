
# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import re
import traceback
from typing import TYPE_CHECKING, cast

# * Third Party Imports --------------------------------------------------------------------------------->
from docutils import nodes
from sphinx.util import logging as sphinx_logging
from sphinx.util.nodes import clean_astext
from sphinx.domains.std import StandardDomain
from pathlib import Path
# * Type-Checking Imports --------------------------------------------------------------------------------->
if TYPE_CHECKING:
    from sphinx.application import Sphinx as SphinxApplication

# endregion [Imports]


NORMALIZE_REPLACE_REGEX = re.compile(r"[ \_\.\:\;\[\]\(\)\{\}]")
NORMALIZE_REMOVE_REGEX = re.compile(r"[\!\"\'\§\%\&]")

THIS_FILE_DIR = Path(__file__).parent.absolute()


def normalize_id(in_ref_name: str) -> str:
    in_ref_name = in_ref_name.strip().casefold()

    in_ref_name = NORMALIZE_REMOVE_REGEX.sub("", in_ref_name)
    in_ref_name = NORMALIZE_REPLACE_REGEX.sub("-", in_ref_name)

    return in_ref_name


def register_cards_as_label(app: "SphinxApplication", document: nodes.Node) -> None:

    if getattr(app.config, "cards_as_labels", False) is False:
        return

    domain = cast(StandardDomain, app.env.get_domain('std'))
    for _node in document.findall(nodes.container):
        _node: nodes.Node
        for node in _node.findall():

            try:

                if "sd-card-title" not in node["classes"]:
                    continue
                docname = app.env.docname
                title = node.astext()
                ref_name = getattr(title, 'rawsource', title)
                if app.config.autosectionlabel_prefix_document:
                    name = nodes.fully_normalize_name(docname + ':' + ref_name)
                else:
                    name = nodes.fully_normalize_name(ref_name)
                try:
                    ids = node["ids"]
                except KeyError:
                    ids = []

                ids.append(normalize_id(ref_name))
                node["ids"] = ids

                labelid = next(iter(node['ids']), "")

                try:
                    sectname = node["rel_sect_name"]
                except KeyError:
                    sectname = clean_astext(node)
                    if docname == "links":
                        sectname = f"{sectname} Links"

                sphinx_logging.getLogger(__name__).debug('section "%s" gets labeled as "%s"',
                                                         ref_name, name,
                                                         location=node, type='autosectionlabel', subtype=docname)

                if name not in domain.labels:
                    # sphinx_logging.getLogger(__name__).warning('duplicate label %s, other instance in %s',
                    #                                            name, app.env.doc2path(domain.labels[name][0]),
                    #                                            location=node, type='autosectionlabel', subtype=docname)

                    domain.anonlabels[name] = docname, labelid
                    domain.labels[name] = docname, labelid, sectname

            except Exception as e:
                if "string indices must be integers, not 'str'" in e.args:
                    continue
                traceback.print_exc()
                continue
