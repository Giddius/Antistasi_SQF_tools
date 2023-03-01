"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
from typing import Callable
from pathlib import Path

# * Third Party Imports --------------------------------------------------------------------------------->
import requests
from yarl import URL

# endregion [Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion [Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion [Constants]


class FileToPreload:
    chunk_size = 250 * 1000  # KB

    def __init__(self, url: str, target_folder: str, target_name: str = None, content_modification_func: Callable[[str], str] = None) -> None:
        self.url: URL = URL(url)
        self.target_folder = target_folder
        self.target_name = target_name or self.url.name
        self.content_modification_func = content_modification_func

    @classmethod
    def set_chunk_size(cls, new_chunk_size: int):
        cls.chunk_size = new_chunk_size

    def get_full_path(self, source_dir: Path) -> Path:
        return source_dir.joinpath(self.target_folder, self.target_name).resolve()

    def get_content(self) -> str:
        content = ""
        with requests.get(self.url) as response:
            response.raise_for_status()
            for chunk in response.iter_content(self.chunk_size, decode_unicode=True):
                content += chunk
        if self.content_modification_func is not None:
            content = self.content_modification_func(content)
        return content

    def write_content(self, content: str, source_dir: Path) -> Path:
        full_target_path = source_dir.joinpath(self.target_folder, self.target_name).resolve()
        full_target_path.parent.mkdir(exist_ok=True, parents=True)
        full_target_path.write_text(content, encoding='utf-8', errors='ignore')
        return full_target_path

    def preload(self, source_dir: Path) -> Path:
        content = self.get_content()
        return self.write_content(content=content, source_dir=source_dir)

    # region [Main_Exec]
if __name__ == '__main__':
    pass
# endregion [Main_Exec]
