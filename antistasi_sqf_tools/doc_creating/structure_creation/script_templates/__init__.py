from pathlib import Path
from typing import Any, Union, TYPE_CHECKING
import os
from jinja2 import Environment, BaseLoader, Template
from functools import cached_property

if TYPE_CHECKING:
    from antistasi_sqf_tools.doc_creating.structure_creation.structure_creator import StructureCreator


SCRIPT_TEMPLATES_FOLDER = Path(__file__).parent.absolute()


class ScriptTemplate:
    jinja_env = Environment(loader=BaseLoader)

    def __init__(self, path: Union[str, os.PathLike]) -> None:
        self.path = Path(path).resolve()
        self.relative_target_path: str = None

    @cached_property
    def template(self) -> Template:
        return self.jinja_env.from_string(self.path.read_text(encoding='utf-8', errors='ignore'))

    def set_relative_target_path(self, relative_target_path: str) -> None:
        self.relative_target_path = relative_target_path

    def render(self, creator: "StructureCreator") -> Path:
        if self.relative_target_path is None:
            raise ValueError(f"Cannot render with relative_target_path={self.relative_target_path!r}.")

        full_path = creator.base_folder.joinpath(self.relative_target_path)
        with full_path.open("w", encoding='utf-8', errors='ignore') as f:
            f.write(self.template.render(**creator.render_kwargs))
        return full_path

    def __fspath__(self) -> str:
        return str(self.path)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(path={self.path!r}, relative_target_path={self.relative_target_path!r})"


def collect_all_script_templates() -> dict[str, ScriptTemplate]:
    all_templates = {}
    for file in SCRIPT_TEMPLATES_FOLDER.iterdir():
        if file.stem == "__init__":
            continue
        all_templates[file.stem.casefold()] = ScriptTemplate(path=file)
    return all_templates


ALL_SCRIPT_TEMPLATES = collect_all_script_templates()


def get_script_template(name: str) -> ScriptTemplate:
    mod_name = name.split(".")[0].casefold()
    template = ALL_SCRIPT_TEMPLATES.get(mod_name, None)
    if template is None:
        raise FileNotFoundError(f"Unable to find the script template with the name {name!r}.")
    return template
