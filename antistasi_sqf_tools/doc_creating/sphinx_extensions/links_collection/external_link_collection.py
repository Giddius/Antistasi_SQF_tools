"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import os
import sys
import json
from typing import TYPE_CHECKING, Union, Optional, TypedDict
from pathlib import Path
from functools import total_ordering
from collections.abc import Callable, Iterable

# * Third Party Imports --------------------------------------------------------------------------------->
from yarl import URL
from sphinx.util import logging as sphinx_logging

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

# * Local Imports --------------------------------------------------------------------------------------->
from antistasi_sqf_tools.doc_creating.utils.string_helper import StringCase, StringCaseConverter

from .external_link import TARGET_STRING_TYPE, FixedExternalLink

# * Type-Checking Imports --------------------------------------------------------------------------------->
if TYPE_CHECKING:
    ...

# endregion [Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion [Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion [Constants]


@total_ordering
class FixedExternalLinkCategory:

    def __init__(self,
                 name: str) -> None:

        self.name = self.normalize_name(name)
        self._links: list["FixedExternalLink"] = []

    @classmethod
    def normalize_name(cls, name: str) -> str:
        return StringCaseConverter.convert_to(name, StringCase.SNAKE)

    @classmethod
    def prettify_name(cls, name: str) -> str:
        return StringCaseConverter.convert_to(name, StringCase.TITLE)

    @property
    def pretty_name(self) -> str:
        return self.prettify_name(self.name)

    @property
    def links(self) -> list[FixedExternalLink]:
        sorted_links = sorted(self._links, key=lambda x: x.name.casefold().strip())
        _out = [link for link in sorted_links if link.position is None]

        for link in [_link for _link in sorted_links if _link.position is not None]:
            try:
                _out.insert(link.position, link)
            except Exception:
                _out.append(link)

        return _out

    @property
    def link_file_links(self) -> list[FixedExternalLink]:
        return [link for link in self.links if "not_in_linkfile" not in link.flags]

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FixedExternalLinkCategory):
            return NotImplemented

        return self.name == other.name and len(self.links) == len(other.links)

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, FixedExternalLinkCategory):
            return NotImplemented
        if self.name == FixedExternalLinkCollection.default_category_name:
            return False
        if len(self.links) == len(other.links):
            return sorted([self.name, other.name])[0] != self.name

        return len(self.links) < len(other.links)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r})"


class LinkData(TypedDict):
    name: str
    url: str
    aliases: Optional[Iterable[str]]
    position: Optional[int]
    category: Optional[str]
    description: Optional[str]
    target: Optional["TARGET_STRING_TYPE"]


class FixedExternalLinkCollection:
    default_category_name: str = "general"

    default_sort_func = None

    def __init__(self, sort_func: Callable[[FixedExternalLinkCategory], tuple] = None) -> None:
        self.sort_func = sort_func or self.default_sort_func
        self._categories: set[FixedExternalLinkCategory] = []

    @property
    def categories(self) -> tuple[FixedExternalLinkCategory]:
        return tuple(reversed(sorted(self._categories, key=self.sort_func)))

    @property
    def link_file_categories(self) -> tuple[FixedExternalLinkCategory]:
        return [cat for cat in self.categories if len(cat.link_file_links) > 0]

    @property
    def links(self) -> tuple[FixedExternalLink]:
        _out = []
        for category in self.categories:
            _out += list(category.links)
        return tuple(_out)

    def get_category_by_name(self, name: str) -> FixedExternalLinkCategory:
        mod_name = FixedExternalLinkCategory.normalize_name(name)

        category = next((c for c in self._categories if c.name == mod_name), None)
        if category is None:
            raise KeyError(f"No category named {name!r} ({mod_name!r}).")
        return category

    def get_link_by_name(self, name: str) -> Optional[FixedExternalLink]:
        return next((link for link in self.links if name.casefold() in {link.name.casefold()}.union({alias_name.casefold() for alias_name in link.aliases})), None)

    def get_link_by_url(self, url: Union[str, URL]) -> Optional[FixedExternalLink]:
        return next((link for link in self.links if link.url == URL(url)), None)

    def add_category(self, category_name: str) -> FixedExternalLinkCategory:

        try:
            category = self.get_category_by_name(category_name)
        except KeyError:
            category = FixedExternalLinkCategory(category_name)
            self._categories.append(category)

        return category

    def add_link(self, link_data: LinkData) -> None:
        category_name = link_data.pop("category", self.default_category_name)

        category = self.add_category(category_name)

        link = self.get_link_by_url(link_data["url"])

        if link is None:
            link = FixedExternalLink(**link_data)
            link._add_default_aliases()
            link.category = category
            category._links.append(link)

        elif link.category is not category:
            raise ValueError(f"Cannot have one link in two different categories, {category!r} and {link.category!r} for {link.url!r}.")

        else:

            link.aliases.update([link_data["name"]] + link_data.get("aliases", []))

            if link.position is None or (link_data.get("position", None) is not None and link_data["position"] < link.position):
                link.position = link_data.get("position", None)

            if link.description is None:
                link.description = link_data.get("description", None)

    def load_links_from_file(self, file_path: Union[str, os.PathLike, Path, None]) -> Self:
        if file_path is None:
            return self

        try:
            file_path = Path(file_path).resolve()

            with file_path.open("r", encoding='utf-8', errors='ignore') as f:
                for link_data_item in (LinkData(**link_data) for link_data in json.load(f)):
                    self.add_link(link_data_item)
        except (FileNotFoundError, OSError) as e:
            logger = sphinx_logging.getLogger(__name__)
            logger.warning("Encountered error %r (%r) while trying to load links from file %r.", e, e.args, file_path, location="")

        return self

    def add_links(self, links: Iterable[LinkData]) -> Self:
        for link in links:
            self.add_link(link)

        return self

    def get_link_file_data(self) -> list[tuple["FixedExternalLinkCategory", list["FixedExternalLink"]]]:
        data = []
        for category in self.link_file_categories:
            data.append((category, category.link_file_links))

        return data

        # region [Main_Exec]
if __name__ == '__main__':
    ...
# endregion [Main_Exec]
