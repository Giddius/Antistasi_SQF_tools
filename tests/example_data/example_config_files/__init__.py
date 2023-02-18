# region [Imports]

from pathlib import Path

# endregion [Imports]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion [Constants]


FILES: dict[str, Path] = {p.name.casefold(): p for p in THIS_FILE_DIR.iterdir() if p.is_file() and p.name != "__init__.py"}
