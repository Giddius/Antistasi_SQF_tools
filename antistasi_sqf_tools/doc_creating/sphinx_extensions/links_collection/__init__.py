from .external_link_collection import ExternalLink, ExternalLinkCategory, ExternalLinkCollection
from .link_file_creation import build_link_file
import os
from typing import TYPE_CHECKING, Union, Optional, cast
from pathlib import Path, WindowsPath, PurePath
from sphinx.util.docutils import SphinxRole, SphinxDirective
from docutils.parsers.rst import directives
from sphinx.util.nodes import set_source_info
from docutils.parsers.rst.roles import set_classes
from time import sleep
import random
from docutils import nodes
from pprint import pprint
from yarl import URL
import docutils
import re
from sphinx.util import logging as sphinx_logging
from sphinx.domains.std import StandardDomain
from sphinx.util.nodes import clean_astext
from sphinx_design.cards import CardDirective

import traceback
from antistasi_sqf_tools import __version__
from sphinx.util import requests as sphinx_requests
import jinja2
from sphinx_design.badges_buttons import create_bdg_classes
if TYPE_CHECKING:
    from sphinx.application import Sphinx as SphinxApplication
    from sphinx.config import Config as SphinxConfig
    from docutils.parsers.rst.states import Inliner

# region [Constants]

EXTERNAL_LINK_FILE_CONFIG_NAME = "external_link_file"

EXTERNAL_LINK_DEFAULT_TARGET_CONFIG_NAME = "external_link_default_target"

EXTERNAL_LINK_BUILD_LINK_FILE_CONFIG_NAME = "external_link_build_link_file"

EXTERNAL_LINK_BUILD_LINK_FILE_TEMPLATE_NAME = "external_link_build_link_file_template_name"

DEFAULT_LINK_FILE_NAME = "links.json"

EXTERNAL_LINKS_EXTRA_LINKS_CONFIG_NAME = "external_link_extra_links"

DEFAULT_BUILD_LINKS_FILE_TEMPLATE_NAME = "links_template.jinja_rst"

# endregion [Constants]


class ExternalLinkRole(SphinxRole):
    link_collection: ExternalLinkCollection = None
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
    if getattr(app.config, EXTERNAL_LINK_BUILD_LINK_FILE_CONFIG_NAME) is False:
        return
    build_link_file(app=app, link_collection=ExternalLinkRole.link_collection, template_name=getattr(app.config, EXTERNAL_LINK_BUILD_LINK_FILE_TEMPLATE_NAME))


def resolve_link_file_path(source_dir: str, config: "SphinxConfig") -> Optional[Path]:

    def locate_link_file():
        _source_dir = Path(source_dir).resolve()
        for dirname, folder_list, file_list in os.walk(_source_dir):
            for file in file_list:
                if file.casefold() == DEFAULT_LINK_FILE_NAME:
                    return Path(dirname, file).resolve()

    return getattr(config, EXTERNAL_LINK_FILE_CONFIG_NAME) or locate_link_file()


def setup_link_collection(app: "SphinxApplication", config: "SphinxConfig"):
    default_target_attribute_value = getattr(config, EXTERNAL_LINK_DEFAULT_TARGET_CONFIG_NAME)

    ExternalLink.set_default_target_attribute(default_target_attribute_value)

    link_collection = ExternalLinkCollection()

    link_file = resolve_link_file_path(app.srcdir or app.confdir, config)
    if link_file is None:
        logger = sphinx_logging.getLogger(__name__)
        logger.warning("Unable to resolve link-file (link_file=%r)", link_file, location="")

    link_collection.load_links_from_file(link_file).add_links(getattr(app.config, EXTERNAL_LINKS_EXTRA_LINKS_CONFIG_NAME))
    ExternalLinkRole.link_collection = link_collection


def setup(app: "SphinxApplication"):
    app.add_config_value(EXTERNAL_LINK_FILE_CONFIG_NAME, None, '', types=[type(None), str, Path, WindowsPath, PurePath])
    app.add_config_value(EXTERNAL_LINK_DEFAULT_TARGET_CONFIG_NAME, "NEW_TAP", '', types=[str])
    app.add_config_value(EXTERNAL_LINK_BUILD_LINK_FILE_CONFIG_NAME, True, '', types=[bool])
    app.add_config_value(EXTERNAL_LINK_BUILD_LINK_FILE_TEMPLATE_NAME, DEFAULT_BUILD_LINKS_FILE_TEMPLATE_NAME, "", types=[str])
    app.add_config_value(EXTERNAL_LINKS_EXTRA_LINKS_CONFIG_NAME, tuple(), "", types=[list, tuple, set])

    app.add_role("la", ExternalLinkRole())
    app.add_role("l", ExternalLinkRole(use_base_name_always=True))
    app.add_role("steam", SteamLink())

    app.connect("config-inited", setup_link_collection)
    app.connect("builder-inited", handle_link_file)

    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
