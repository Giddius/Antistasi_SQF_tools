"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import os
import random
from time import sleep
from typing import Union, Callable, Iterable, Optional, Generator
from pathlib import Path
from datetime import datetime, timezone
from functools import partial
from threading import Semaphore
from collections import defaultdict

# * Third Party Imports --------------------------------------------------------------------------------->
import requests
from yarl import URL
from dotenv import load_dotenv
from github import Github
from github.Branch import Branch
from github.Commit import Commit
from github.GitTree import GitTree
from github.Repository import Repository


# endregion [Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion [Logging]

# region [Constants]
load_dotenv("github.env")
THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion [Constants]


class DelayedSemaphore(Semaphore):

    def __init__(self, value: int = 1, delay: Union[int, float, Callable[[], float]] = None) -> None:
        super().__init__(value)
        self._delay = delay

    def _resolve_delay(self) -> None:
        if self._delay is None:
            return

        if isinstance(self._delay, (int, float)):
            sleep(self._delay)

        else:
            sleep(self._delay())

    def release(self, n: int = 1) -> None:
        self._resolve_delay()
        return super().release(n)


def parse_last_modifed(in_last_modified: str) -> datetime:
    month_conversion_table = {"jan": 1,
                              "feb": 2,
                              "mar": 3,
                              "apr": 4,
                              "may": 5,
                              "jun": 6,
                              "jul": 7,
                              "aug": 8,
                              "sep": 9,
                              "oct": 10,
                              "nov": 11,
                              "dec": 12,
                              "dez": 12}
    cleaned_last_modified = in_last_modified.split(",")[-1].removesuffix("GMT").strip()
    raw_day, raw_month, raw_year, raw_time = cleaned_last_modified.split()

    day = int(raw_day)
    month = month_conversion_table.get(raw_month.casefold())
    year = int(raw_year)
    hour, minute, second = (int(i.strip()) for i in raw_time.split(":"))
    return datetime(year=year, month=month, day=day, hour=hour, minute=minute, second=second, tzinfo=timezone.utc)


GITHUB_URL = URL("https://github.com")

GITHUB_DONWLOAD_BASE_URL = URL("https://raw.githubusercontent.com")


class GitHubItem:

    def __init__(self,
                 name: str,
                 path: Path,
                 url: URL,
                 last_modified: datetime,
                 sha: str,
                 size: int,
                 repo: "GithubRepo") -> None:
        self.name = name
        self.path = path
        self.url = url
        self.last_modified = last_modified
        self.sha = sha
        self.size = size
        self.repo = repo
        self._parent: "GithubFolder" = None

    @property
    def parent(self) -> Optional["GithubFolder"]:
        return self._parent

    @property
    def parent_folder_path(self) -> Optional[Path]:
        if self.name == "ROOT":
            return None
        return self.path.parent

    def __hash__(self) -> int:
        return hash(self.sha)

    def __repr__(self) -> str:
        """
        Basic Repr
        !REPLACE!
        """
        return f'{self.__class__.__name__}(name={self.name!r}, path={self.path.as_posix()!r}, last_modified={self.last_modified!r}, size={self.size!r}, parent={self.parent!r})'


class GithubFile(GitHubItem):

    def __init__(self,
                 name: str,
                 path: Path,
                 url: URL,
                 download_url: URL,
                 last_modified: datetime,
                 sha: str,
                 size: int,
                 repo: "GithubRepo") -> None:
        super().__init__(name=name,
                         path=path,
                         url=url,
                         last_modified=last_modified,
                         sha=sha,
                         size=size,
                         repo=repo)
        self.download_url = download_url

    def get_content(self) -> str:
        with self.repo.download_semaphore:
            with requests.get(self.download_url, timeout=None) as response:
                return response.text

    def download(self, target_folder: Path) -> Path:
        out_path = target_folder.joinpath(self.name)
        out_path.write_text(self.get_content(), encoding='utf-8', errors='ignore')

    def __repr__(self) -> str:
        """
        Basic Repr
        !REPLACE!
        """
        return f'{self.__class__.__name__}(name={self.name!r},path={self.path.as_posix()!r}, last_modified={self.last_modified!r}, size={self.size!r}, parent={self.parent!r})'


class GithubFolder(GitHubItem):

    def __init__(self,
                 name: str,
                 path: Path,
                 url: URL,
                 last_modified: datetime,
                 sha: str,
                 repo: "GithubRepo") -> None:
        super().__init__(name=name,
                         path=path,
                         url=url,
                         last_modified=last_modified,
                         sha=sha,
                         size=None,
                         repo=repo)

        self.children: list[Union["GithubFile", "GithubFolder"]] = []

    def add_child(self, child: Union[GithubFile, "GithubFolder"]):
        child._parent = self
        self.children.append(child)

    def walk(self) -> Generator[Union[GithubFile, "GithubFolder"], None, None]:
        def _recursive_walk(folder: GithubFolder):
            yield folder
            for sub_item in folder.children:
                if isinstance(sub_item, GithubFile):
                    yield sub_item
                elif isinstance(sub_item, GithubFolder):
                    yield from _recursive_walk(sub_item)
        yield from _recursive_walk(self)


class GithubItemsHolder:

    def __init__(self, github_items: Iterable[Union[GithubFile, GithubFolder]]) -> None:
        self.github_items = tuple(github_items)
        self.folder_items = {i.path: i for i in self.github_items if isinstance(i, GithubFolder)}
        self.file_name_map, self.file_path_map = self._make_file_map()
        self._item_path_map = {i.path: i for i in self.github_items}

    def _make_file_map(self) -> tuple[dict[str, GithubFile], dict[Path, GithubFile]]:
        name_map = defaultdict(list)
        path_map = {}
        for item in self.github_items:
            if not isinstance(item, GithubFile):
                continue
            name_map[item.name.casefold()].append(item)
            path_map[item.path] = item
        return name_map, path_map

    @property
    def root(self) -> GithubFolder:
        return next(i for i in self.folder_items if i.name.casefold() == "root")

    @property
    def read_me(self) -> GithubFile:
        return self.file_path_map.get(Path("readme.md"))

    @property
    def changelog(self) -> GithubFile:
        try:
            return self.file_name_map.get("changelog.txt", [])[0]
        except IndexError:
            return self.file_name_map.get(Path("changelog.rst"))[0]

    def __getitem__(self, path: Path) -> Union[GithubFile, GithubFolder]:
        return self._item_path_map[path]

    def __len__(self) -> int:
        return len(self.github_items)


class GithubRepo:
    download_semaphore = DelayedSemaphore(1, partial(random.randint, 0, 3))

    def __init__(self, owner_name: str, repo_name: str, branch_name: str = None, github_client: Github = None) -> None:
        self._owner_name = owner_name
        self._repo_name = repo_name
        self._branch_name = branch_name
        self._full_identifier = f"{self._owner_name}/{self._repo_name}"
        self._repo_url = GITHUB_URL / self._owner_name / self._repo_name

        self.github_client: Github = github_client or self.get_github_client()
        self._repo: Repository = self.github_client.get_repo(self._full_identifier)
        self._branch: Branch = None
        self._git_tree: GitTree = None
        self._file_items: GithubItemsHolder = None

    def initialize_branch(self) -> "GithubRepo":
        self._branch = self._repo.get_branch(self.branch_name)
        self._git_tree = self._get_git_tree()
        self._file_items = self._get_file_items()
        return self

    @staticmethod
    def get_github_client() -> Github:
        token = os.getenv("_DOC_CREATION_GITHUB_TOKEN", None)
        return Github(token)

    def _get_file_items(self) -> tuple[Union[GithubFile, GithubFolder]]:

        root = GithubFolder(name="ROOT", path=Path("."), url=self.base_file_url, last_modified=parse_last_modifed(self.git_tree.last_modified), sha=self.git_tree.sha, repo=self)
        collected_items = [root]
        for item in self.git_tree.tree:

            name = item.path.split("/")[-1]
            url = self.base_file_url / item.path
            last_modifed = parse_last_modifed(item.last_modified)
            sha = str(item.sha)
            size = item.size
            path = Path(item.path)
            if item.type == "tree":
                github_item = GithubFolder(name=name, path=path, url=url, last_modified=last_modifed, sha=sha, repo=self)
            elif item.type == "blob":
                download_url = self.download_base_url / item.path
                github_item = GithubFile(name=name, path=path, download_url=download_url, url=url, last_modified=last_modifed, sha=sha, size=size, repo=self)

            collected_items.append(github_item)

        folder_dict = {i.path: i for i in collected_items if isinstance(i, GithubFolder)}
        for collected_item in collected_items:

            parent_item = folder_dict.get(collected_item.parent_folder_path, None)
            if parent_item is not None:

                parent_item.add_child(collected_item)

        return GithubItemsHolder(github_items=collected_items)

    def _get_git_tree(self) -> GitTree:
        latest_sha = self.latest_commit.sha
        return self._repo.get_git_tree(latest_sha, True)

    def get_file_by_name(self, name: str) -> Optional[list[GithubFile]]:
        mod_name = name.casefold()
        return self._file_items.file_name_map.get(mod_name, None)

    @property
    def has_token(self) -> bool:
        return self.github_client.oauth_scopes is not None

    @property
    def rate_limit_left(self) -> int:
        return self.github_client.rate_limiting[0]

    @property
    def branch_name(self) -> str:
        if self._branch_name is None:
            self._branch_name = self._repo.default_branch
        return self._branch_name

    @branch_name.setter
    def branch_name(self, name: Union[None, str]) -> None:
        self._branch_name = name
        self.initialize_branch()

    @property
    def base_file_url(self) -> URL:
        return self._repo_url / "blob" / self.branch_name

    @property
    def download_base_url(self) -> URL:
        return GITHUB_DONWLOAD_BASE_URL / self._owner_name / self._repo_name / self.branch_name

    @property
    def latest_commit(self) -> Commit:
        return self._branch.commit

    @property
    def branch(self) -> Branch:
        return self._branch

    @property
    def git_tree(self) -> GitTree:
        return self._git_tree

    def __repr__(self) -> str:
        """
        Basic Repr
        !REPLACE!
        """
        return f'{self.__class__.__name__}(owner_name={self._owner_name!r}, repo_name={self._repo_name!r}, branch_name={self.branch_name!r})'


# region [Main_Exec]
if __name__ == '__main__':
    x = GithubRepo("official-antistasi-community", "A3-Antistasi").initialize_branch()

    print(x._file_items.read_me.get_content())
    print(x._file_items.changelog.get_content())
# endregion [Main_Exec]
