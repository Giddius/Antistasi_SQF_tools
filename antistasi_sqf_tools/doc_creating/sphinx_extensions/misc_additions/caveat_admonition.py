
# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
from typing import TYPE_CHECKING

# * Third Party Imports --------------------------------------------------------------------------------->
from docutils import nodes
from docutils.parsers.rst.directives.admonitions import BaseAdmonition

# * Type-Checking Imports --------------------------------------------------------------------------------->
if TYPE_CHECKING:
    pass

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
