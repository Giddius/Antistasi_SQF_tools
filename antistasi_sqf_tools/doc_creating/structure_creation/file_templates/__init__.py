from pathlib import Path
from typing import Any, Union, TYPE_CHECKING
import os
from jinja2 import Environment, BaseLoader, Template
from functools import cached_property

if TYPE_CHECKING:
    from antistasi_sqf_tools.doc_creating.structure_creation.structure_creator import StructureCreator


FILE_TEMPLATES_FOLDER = Path(__file__).parent.absolute()


class FileTemplate:
    jinja_env = Environment(loader=BaseLoader)

    def __init__(self, path: Union[str, os.PathLike], relative_path: str) -> None:
        self.path = Path(path).resolve()
        self.relative_target_path = relative_path

    @cached_property
    def template(self) -> Template:
        return self.jinja_env.from_string(self.path.read_text(encoding='utf-8', errors='ignore'))

    def render(self, creator: "StructureCreator") -> Path:
        full_path = creator._temp_base_folder.joinpath(self.relative_target_path)
        with full_path.open("w", encoding='utf-8', errors='ignore') as f:
            f.write(self.template.render(**creator.render_kwargs))
        return full_path

    def __fspath__(self) -> str:
        return str(self.path)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(path={self.path!r}, relative_target_path={self.relative_target_path!r})"


def get_file_template(name: str, relative_path: str) -> FileTemplate:
    mod_name = name.casefold()
    for file in FILE_TEMPLATES_FOLDER.iterdir():
        if file.name.casefold() == mod_name:

            return FileTemplate(path=file, relative_path=relative_path)

    raise FileNotFoundError(f"Unable to find the script template with the name {name!r}.")
