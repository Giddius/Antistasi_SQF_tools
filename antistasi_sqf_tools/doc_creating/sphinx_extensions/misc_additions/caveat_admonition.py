
# region [Imports]
from docutils import nodes
from docutils.parsers.rst.directives.admonitions import BaseAdmonition
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sphinx.application import Sphinx as SphinxApp

# endregion [Imports]


class caveat(nodes.Admonition, nodes.Element):
    title = "CAVE"


def visit_caveat_node(self, node: nodes.Node):

    name = getattr(node, "name", node.__class__.__name__)
    title = getattr(node, "title", name.title())

    self.body.append(self.starttag(
        node, 'div', CLASS=('admonition ' + name)))
    if name:
        node.insert(0, nodes.title(name, title))


def depart_caveat_node(self, node: nodes.Node):
    self.body.append('</div>\n')


class Caveat(BaseAdmonition):
    node_class = caveat
