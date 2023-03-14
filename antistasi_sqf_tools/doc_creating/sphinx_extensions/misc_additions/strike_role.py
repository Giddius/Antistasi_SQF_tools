
# region [Imports]

# * Third Party Imports --------------------------------------------------------------------------------->
import docutils
from docutils import nodes
from sphinx.writers.html5 import HTML5Translator
from docutils.parsers.rst.states import Inliner

# endregion [Imports]


class strike_node(nodes.Inline, nodes.TextElement):
    tag_name = "span"


def html_visit_strike_node(self: HTML5Translator, node: nodes.Node) -> None:
    self.body.append(self.starttag(node, node.tag_name, '', classes=["strike"]))


def html_depart_strike_node(self: HTML5Translator, node: nodes.Node) -> None:
    self.body.append(f'</{node.tag_name}>')


def strike_role(typ: str,
                rawtext: str,
                text: str,
                lineno: int,
                inliner: Inliner,
                options: dict = None,
                content: list[str] = None) -> tuple[list[nodes.Node], list[nodes.system_message]]:

    print(f"{typ=}", flush=True)
    options = options or {}
    content = content or []
    env = inliner.document.settings.env

    if not getattr(env.app.builder, "format", "").casefold() == "html":
        # Builder is not supported, fallback to text.
        return [nodes.Text(docutils.utils.unescape(text))], []

    node = strike_node(rawtext, docutils.utils.unescape(text))
    node['docname'] = env.docname
    node["lineno"] = lineno
    return [node], []
