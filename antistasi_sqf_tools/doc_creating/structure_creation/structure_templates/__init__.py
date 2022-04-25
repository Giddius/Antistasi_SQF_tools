from pathlib import Path
import json
from typing import Union
import os
from functools import cached_property
STRUCTURE_TEMPLATES_FOLDER = Path(__file__).parent.absolute()
from antistasi_sqf_tools.doc_creating.structure_creation.file_templates import get_file_template, FileTemplate


class StructureTemplate:

    def __init__(self, path: Union[str, os.PathLike]) -> None:
        self._path = Path(path).resolve()
        self._folder: list[str] = None
        self._files: list[FileTemplate] = None

    def _load(self) -> None:
        content = self.get_content()
        self._folder = content.get("folder", [])
        self._files = [get_file_template(name=item["name"], relative_path=item["path"]) for item in content.get("files", [])]

    @property
    def path(self) -> Path:
        return self._path

    @property
    def folder(self) -> list[str]:
        if self._folder is None:
            self._load()
        return self._folder

    @property
    def files(self) -> list[FileTemplate]:
        if self._files is None:
            self._load()
        return self._files

    def get_content(self) -> dict:
        with self.path.open("r", encoding='utf-8', errors='ignore') as f:
            return json.load(f)

    def items(self):
        return self.get_content().items()

    def keys(self):
        return self.get_content().keys()

    def values(self):
        return self.get_content().values()

    def __fspath__(self) -> str:
        return str(self.path)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(path={self.path!r})"


def collect_all_structure_templates() -> dict[str, StructureTemplate]:
    all_templates = {}
    for file in STRUCTURE_TEMPLATES_FOLDER.iterdir():
        if file.suffix != ".json":
            continue
        all_templates[file.stem.casefold()] = StructureTemplate(path=file)
    return all_templates


ALL_STRUCTURE_TEMPLATES = collect_all_structure_templates()


def get_structure_template(name: str) -> StructureTemplate:
    mod_name = name.split(".")[0].casefold()
    for file in STRUCTURE_TEMPLATES_FOLDER.iterdir():
        if file.stem.casefold() == mod_name:
            return StructureTemplate(path=file)

    raise FileNotFoundError(f"Unable to find the structure template with the name {name!r}.")
