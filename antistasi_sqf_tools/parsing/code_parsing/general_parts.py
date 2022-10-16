"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
from pathlib import Path

# * Third Party Imports --------------------------------------------------------------------------------->
import pyparsing as ppa
from pprint import pformat
# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class GeneralGrammarParts:
    __slots__ = ("single_quote",
                 "double_quote",

                 "comma",
                 "semi_colon",
                 "colon",

                 "equals_sign",
                 "exclamation_mark",
                 "octothorp",
                 "backslash",
                 "forward_slash",
                 "greater_than",
                 "less_than",
                 "pipe",

                 "parentheses_open",
                 "parentheses_close",
                 "brackets_open",
                 "brackets_close",
                 "braces_open",
                 "braces_close")

    def __init__(self) -> None:
        self.single_quote = ppa.Suppress("'")
        self.double_quote = ppa.Suppress('"')

        self.comma = ppa.Suppress(",")
        self.semi_colon = ppa.Suppress(";")
        self.colon = ppa.Suppress(":")

        self.equals_sign = ppa.Suppress("=")
        self.exclamation_mark = ppa.Suppress("!")
        self.octothorp = ppa.Suppress("#")
        self.backslash = ppa.Suppress("\\")
        self.forward_slash = ppa.Suppress("/")
        self.greater_than = ppa.Suppress("<")
        self.less_than = ppa.Suppress(">")
        self.pipe = ppa.Suppress("|")

        self.parentheses_open = ppa.Suppress("(")
        self.parentheses_close = ppa.Suppress(")")
        self.brackets_open = ppa.Suppress("[")
        self.brackets_close = ppa.Suppress("]")
        self.braces_open = ppa.Suppress("{")
        self.braces_close = ppa.Suppress("}")

    def __getitem__(self, name: str) -> ppa.ParserElement:
        try:
            return getattr(self, name)
        except AttributeError as e:
            raise KeyError(f"Unknown key {name!r}.") from e

    def __repr__(self) -> str:
        """
        Basic Repr
        !REPLACE!
        """
        return f'{self.__class__.__name__}'

# region[Main_Exec]


if __name__ == '__main__':
    pass

# endregion[Main_Exec]
