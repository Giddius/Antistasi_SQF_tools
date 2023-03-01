
# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import os
import re
import random
from time import sleep
from typing import TYPE_CHECKING, Optional, Callable, Union
from pathlib import Path, PurePath, WindowsPath

# * Third Party Imports --------------------------------------------------------------------------------->
import docutils
from yarl import URL
from docutils import nodes
from docutils.statemachine import StringList

from sphinx.util import logging as sphinx_logging
from sphinx.util import requests as sphinx_requests
from sphinx.util.docutils import SphinxRole, SphinxDirective

# * Local Imports --------------------------------------------------------------------------------------->
from antistasi_sqf_tools import __version__

from .link_file_creation import build_link_file
from .external_link_collection import FixedExternalLink, FixedExternalLinkCollection
import sys
if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self
# * Type-Checking Imports --------------------------------------------------------------------------------->




if TYPE_CHECKING:
    from sphinx.config import Config as SphinxConfig
    from sphinx.application import Sphinx as SphinxApplication
    from docutils.parsers.rst.states import Inliner
    import sphinx_design

# endregion [Imports]


# region [Constants]

EXTERNAL_LINK_FILE_CONFIG_NAME = "external_link_file"

EXTERNAL_LINK_DEFAULT_TARGET_CONFIG_NAME = "external_link_default_target"

EXTERNAL_LINK_BUILD_LINK_FILE_CONFIG_NAME = "external_link_build_link_file"

EXTERNAL_LINK_BUILD_LINK_FILE_TEMPLATE_NAME = "external_link_build_link_file_template_name"

DEFAULT_LINK_FILE_NAME = "links.json"

EXTERNAL_LINKS_EXTRA_LINKS_CONFIG_NAME = "external_link_extra_links"

DEFAULT_BUILD_LINKS_FILE_TEMPLATE_NAME = "links_template.jinja_rst"

# endregion [Constants]


class ConfigHolder(dict):

    _settings_name: str = "external_links_settings"

    _default_value = {}

    _sub_value_map: dict[str, Callable] = {}

    _missing_sentinel = object()

    @classmethod
    def from_sphinx_config(cls, sphinx_config: "SphinxConfig") -> Self:
        return cls(getattr(sphinx_config, cls._settings_name))

    def get_sub_value(self, key: str) -> object:
        raw_value = super().get(key, self._missing_sentinel)

        return self._sub_value_map[key](raw_value)

    def __getitem__(self, __key) -> object:
        return self.get_sub_value(__key)

    def get(self, key, default=None) -> object:
        return self.get_sub_value(key)

    @classmethod
    def handle_external_link_default_target(cls, value: Union[str, object]) -> str:
        if value is cls._missing_sentinel:
            return "NEW_TAP"

        return value


ConfigHolder._sub_value_map["external_link_default_target"] = ConfigHolder.handle_external_link_default_target


class FixedExternalLinkRole(SphinxRole):
    link_collection: FixedExternalLinkCollection = None
    link_url: URL
    link_name: str
    target_value: str

    def __init__(self, use_base_name_always: bool = False) -> None:
        super().__init__()
        self.use_base_name_always = use_base_name_always

    def __call__(self,
                 name: str,
                 rawtext: str,
                 text: str,
                 lineno: int,
                 inliner: "Inliner",
                 options: dict = None,
                 content: list[str] = None) -> tuple[list[nodes.Node], list[nodes.system_message]]:

        self.inliner = inliner
        link = self.link_collection.get_link_by_name(text)
        self.link_name = link.name if self.use_base_name_always is True else text
        self.link_url = link.url
        self.target_value = link.target_attribute.html_value
        options = {"classes": ["link-collection-link"]} | (options or {})
        return super().__call__(name=name, rawtext=rawtext, text=text, lineno=lineno, inliner=inliner, options=options, content=content)

    def run(self) -> tuple[list[nodes.Node], list[nodes.system_message]]:
        node = nodes.reference(
            self.rawtext,
            docutils.utils.unescape(self.link_name),
            refuri=str(self.link_url),
            target=self.target_value,
            ** self.options
        )
        self.set_source_info(node)

        return [node], []



class ExternalLinkListItemNode(nodes.container):
    pass

class FixedExternalLinkListDirective(SphinxDirective):
    has_content = False

    def run(self) -> list[nodes.Node]:
        all_nodes = []
        for cat, links in FixedExternalLinkRole.link_collection.get_link_file_data():
            cat_section = nodes.container(ids=[cat.name], classes=["sd-card", "sd-sphinx-override", "sd-mb-3", "sd-shadow-md"], names=[cat.name])
            self.state.nested_parse(StringList([str(cat.pretty_name)]), 1, cat_section)

            self.set_source_info(cat_section)
            cat_def_list = nodes.definition_list(classes=[f"wurst_{cat.name}"])

            for link in links:
                item = nodes.definition_list_item(classes=[f"wuff_{link.name}"])
                term = nodes.term()

                term.append(nodes.reference("", docutils.utils.unescape(str(link.name)), refuri=str(link.url)))
                item.append(term)
                definition = nodes.definition()
                def_paragraph_1 = nodes.paragraph()

                def_paragraph_1.append(nodes.Text(link.description or ""))
                definition.append(def_paragraph_1)

                item.append(definition)
                cat_def_list.append(item)

            cat_section.append(cat_def_list)

            all_nodes.append(cat_section)

        return all_nodes


class SteamLink(SphinxRole):
    workshop_id: str
    workshop_url: str
    workshop_title: str
    target_value: str

    resolved_title_cache: dict[str, str] = {}

    def __init__(self) -> None:
        super().__init__()
        self.base_url = "https://steamcommunity.com/sharedfiles/filedetails/?id="
        self.title_regex = re.compile(r"\<title\>(?P<raw_title>.*?)\</title\>")

    def get_title(self, full_url: str) -> Optional[str]:
        raw_title = None
        text = ""
        response = sphinx_requests.get(full_url, timeout=15)
        response.raise_for_status()
        for line in response.iter_lines(decode_unicode=True):
            text += line
            if match := self.title_regex.search(text):
                raw_title = match.group("raw_title")
                break

        sleep(random.random() + random.random())
        if raw_title is not None:
            return raw_title.removeprefix("Steam Workshop::")

    def __call__(self,
                 name: str,
                 rawtext: str,
                 text: str,
                 lineno: int,
                 inliner: "Inliner",
                 options: dict = None,
                 content: list[str] = None) -> tuple[list[nodes.Node], list[nodes.system_message]]:

        self.inliner = inliner

        self.workshop_id = text
        self.workshop_url = self.base_url + self.workshop_id
        try:
            self.workshop_title = self.__class__.resolved_title_cache[self.workshop_id]
        except KeyError:
            self.workshop_title = self.get_title(self.workshop_url)

            self.__class__.resolved_title_cache[self.workshop_id] = self.workshop_title

        self.target_value = "_blank"

        options = {"classes": ["steam-link"]} | (options or {})
        return super().__call__(name=name, rawtext=rawtext, text=text, lineno=lineno, inliner=inliner, options=options, content=content)

    def run(self) -> tuple[list[nodes.Node], list[nodes.system_message]]:

        node = nodes.reference(
            self.rawtext,
            docutils.utils.unescape(self.workshop_title),
            refuri=self.workshop_url,
            target=self.target_value,
            ** self.options
        )

        self.set_source_info(node)
        return [node], []


def validate_steam_id(in_id: str) -> int:
    in_id = in_id.strip()
    if in_id.isalnum() is False:
        raise ValueError(f"'steam_id' has to be all numeric chars, not {in_id!r}.")
    return in_id


def validate_display_name(in_display_name: str) -> str:
    return in_display_name.strip().title()


def handle_link_file(app: "SphinxApplication"):
    if getattr(app.config, EXTERNAL_LINK_BUILD_LINK_FILE_CONFIG_NAME, False) is False:
        return
    build_link_file(app=app, link_collection=FixedExternalLinkRole.link_collection, template_name=getattr(app.config, EXTERNAL_LINK_BUILD_LINK_FILE_TEMPLATE_NAME))


def resolve_link_file_path(source_dir: str, config: "SphinxConfig") -> Optional[Path]:

    def locate_link_file():
        _source_dir = Path(source_dir).resolve()
        for dirname, folder_list, file_list in os.walk(_source_dir):
            for file in file_list:
                if file.casefold() == DEFAULT_LINK_FILE_NAME:
                    return Path(dirname, file).resolve()

    return getattr(config, EXTERNAL_LINK_FILE_CONFIG_NAME, None) or locate_link_file()


def setup_link_collection(app: "SphinxApplication", config: "SphinxConfig"):
    settings = ConfigHolder.from_sphinx_config(config)
    default_target_attribute_value = settings.get_sub_value("external_link_default_target")

    FixedExternalLink.set_default_target_attribute(default_target_attribute_value)

    link_collection = FixedExternalLinkCollection()

    link_file = resolve_link_file_path(app.srcdir or app.confdir, config)
    if link_file is None:
        logger = sphinx_logging.getLogger(__name__)
        logger.warning("Unable to resolve link-file (link_file=%r)", link_file, location="")

    link_collection.load_links_from_file(link_file).add_links(getattr(app.config, EXTERNAL_LINKS_EXTRA_LINKS_CONFIG_NAME, []))
    FixedExternalLinkRole.link_collection = link_collection


def setup(app: "SphinxApplication"):
    # app.add_config_value(EXTERNAL_LINK_FILE_CONFIG_NAME, None, '', types=[type(None), str, Path, WindowsPath, PurePath])
    # app.add_config_value(EXTERNAL_LINK_DEFAULT_TARGET_CONFIG_NAME, "NEW_TAP", '', types=[str])
    # app.add_config_value(EXTERNAL_LINK_BUILD_LINK_FILE_CONFIG_NAME, True, '', types=[bool])
    # app.add_config_value(EXTERNAL_LINK_BUILD_LINK_FILE_TEMPLATE_NAME, DEFAULT_BUILD_LINKS_FILE_TEMPLATE_NAME, "", types=[str])
    # app.add_config_value(EXTERNAL_LINKS_EXTRA_LINKS_CONFIG_NAME, tuple(), "", types=[list, tuple, set])
    app.add_config_value(ConfigHolder._settings_name, ConfigHolder._default_value, rebuild="", types=(dict,))
    app.add_role("la", FixedExternalLinkRole())
    app.add_role("l", FixedExternalLinkRole(use_base_name_always=True))
    app.add_role("steam", SteamLink())

    app.add_directive("linklist", FixedExternalLinkListDirective)

    app.connect("config-inited", setup_link_collection)
    # app.connect("builder-inited", handle_link_file)

    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
