"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
from enum import Enum
from typing import TYPE_CHECKING, Any, Union, Literal, Optional
from pathlib import Path
from collections.abc import Iterable

# * Third Party Imports --------------------------------------------------------------------------------->
from yarl import URL

# * Type-Checking Imports --------------------------------------------------------------------------------->
if TYPE_CHECKING:
    from .external_link_collection import FixedExternalLinkCategory

# endregion [Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion [Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion [Constants]


TARGET_STRING_TYPE = Literal["_blank", "_self", "_parent", "_top", "SAME_TAP", "NEW_TAP", "SAME_FRAME", "PARENT_FRAME"]


class LinkTarget(Enum):
    SAME_TAP = "_top"
    NEW_TAP = "_blank"
    SAME_FRAME = "_self"
    PARENT_FRAME = "_parent"

    @classmethod
    def _missing_(cls, value: object) -> Any:
        if isinstance(value, str):
            mod_value = value.casefold()
            for member in cls:
                if member.name.casefold() == mod_value:
                    return member
                if member.value.casefold() == mod_value:
                    return member
                if member.value.casefold().removeprefix("_") == mod_value:
                    return member

        return super()._missing_(value)

    @property
    def html_value(self) -> str:
        return str(self.value)


class FixedExternalLink:

    _default_target_attribute: LinkTarget = LinkTarget.NEW_TAP

    def __init__(self,
                 name: str,
                 url: Union[str, URL],
                 aliases: Iterable[str] = None,
                 position: int = None,
                 description: str = None,
                 target: Union[TARGET_STRING_TYPE, LinkTarget] = None,
                 flags: Iterable[str] = None) -> None:

        self.name = name
        self.url = URL(url)
        self.aliases: set[str] = set(aliases) if aliases else set()
        self.position = position
        self.description = description
        self.target_attribute: Optional[LinkTarget] = LinkTarget(target) if target is not None else self._default_target_attribute
        self.category: "FixedExternalLinkCategory" = None
        self.flags = set(flags) if flags is not None else set()

    def _add_default_aliases(self) -> None:
        self.aliases.add(self.name.replace(" ", "_"))
        self.aliases.add(self.name.replace("-", "_"))

    @classmethod
    def set_default_target_attribute(cls, target: Union[TARGET_STRING_TYPE, LinkTarget]) -> None:
        cls._default_target_attribute = LinkTarget(target)

    @property
    def raw_url(self) -> str:
        return str(self.url)

    def __hash__(self) -> int:
        return sum(hash(attr) for attr in [self.url])

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r}, url={self.url!r}, aliases={self.aliases!r}, position={self.position!r},  description={self.description!r})"


# region [Main_Exec]
if __name__ == '__main__':
    pass
# endregion [Main_Exec]
