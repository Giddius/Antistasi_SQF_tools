"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
from pathlib import Path

# endregion [Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion [Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion [Constants]


class BaseConfigClass:

    def __init__(self, name: str, attributes: dict[str, object] = None, nested_classes: list["BaseConfigClass"] = None) -> None:
        self._name = name
        self.attributes = attributes or {}
        self.nested_classes = nested_classes or []

    @property
    def name(self) -> str:
        return self._name

    @property
    def nested_classes_map(self) -> dict[str, "BaseConfigClass"]:
        return {nc.name: nc for nc in self.nested_classes}

    def __getitem__(self, key: str):
        if key in self.attributes:
            return self.attributes[key]

        if key in self.nested_classes_map:
            return self.nested_classes_map[key]

        raise KeyError(f"{self!r} has no attribute or nested class named {key!r}.")

    def __getattr__(self, name: str):
        try:
            return self[name]
        except KeyError as e:
            raise AttributeError(f"{self!r} has no attribute {name!r}.") from e

    def __repr__(self) -> str:
        """
        Basic Repr
        !REPLACE!
        """
        return f'{self.__class__.__name__}(name={self.name!r})'


# region [Main_Exec]
if __name__ == '__main__':
    x = BaseConfigClass(name="Wuff", attributes={"wurst": 14})

    print(x["asas"])

# endregion [Main_Exec]
