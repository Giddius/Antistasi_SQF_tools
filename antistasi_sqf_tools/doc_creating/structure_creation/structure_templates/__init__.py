from pathlib import Path
import json
from typing import Union
import os
from functools import cached_property
STRUCTURE_TEMPLATES_FOLDER = Path(__file__).parent.absolute()
from antistasi_sqf_tools.doc_creating.structure_creation.script_templates import get_script_template, ScriptTemplate


class StructureTemplate:

    def __init__(self, path: Union[str, os.PathLike]) -> None:
        self.path = Path(path).resolve()

    @cached_property
    def content(self) -> dict:
        with self.path.open("r", encoding='utf-8', errors='ignore') as f:
            return json.load(f)

    @property
    def folder(self) -> list[str]:
        return self.content.get("folder", [])

    @property
    def files(self) -> list:
        return self.content.get("files", [])

    @property
    def scripts(self) -> list[ScriptTemplate]:
        scripts = []
        for item in self.content.get("scripts", []):
            template = get_script_template(item["name"])
            template.set_relative_target_path(item["path"])
            scripts.append(template)
        return scripts

    def items(self):
        return self.content.items()

    def keys(self):
        return self.content.keys()

    def values(self):
        return self.content.values()

    def __fspath__(self) -> str:
        return str(self.path)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(path={self.path!r})"


def collect_all_structure_templates() -> dict[str, StructureTemplate]:
    all_templates = {}
    for file in STRUCTURE_TEMPLATES_FOLDER.iterdir():
        if file.stem == "__init__":
            continue
        all_templates[file.stem.casefold()] = StructureTemplate(path=file)
    return all_templates


ALL_STRUCTURE_TEMPLATES = collect_all_structure_templates()


def get_structure_template(name: str) -> StructureTemplate:
    mod_name = name.split(".")[0].casefold()
    template = ALL_STRUCTURE_TEMPLATES.get(mod_name, None)
    if template is None:
        raise FileNotFoundError(f"Unable to find the structure template with the name {name!r}.")
    return template
