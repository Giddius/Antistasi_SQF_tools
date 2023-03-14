"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import os
import atexit
import shutil
from types import TracebackType
from typing import Union, Optional
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import RLock

# * Local Imports --------------------------------------------------------------------------------------->
from antistasi_sqf_tools.errors import TempDirClosedError

# endregion [Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion [Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion [Constants]


class IsolatedTempDir:
    def __init__(self, file_path: Union[str, os.PathLike]) -> None:
        self._original_path = Path(file_path).resolve()
        self._created_temp_dir = TemporaryDirectory(prefix=self._original_path.stem)
        self._temp_path = Path(self._created_temp_dir.name).resolve()
        self._lock = RLock()
        atexit.register(self.cleanup)

    @property
    def closed(self) -> bool:
        with self._lock:
            return self._created_temp_dir is None or self.temp_path is None or self.temp_path.exists() is False

    @property
    def temp_path(self) -> Optional[Path]:
        with self._lock:
            return self._temp_path

    @property
    def original_path(self) -> Path:
        return self._original_path

    def load(self) -> None:
        with self._lock:
            shutil.rmtree(self.temp_path)
            shutil.copytree(self.original_path, self.temp_path, dirs_exist_ok=True)

    def __fspath__(self) -> str:
        return os.fspath(self.temp_path)

    def cleanup(self) -> None:
        with self._lock:
            if self.closed is True:
                return

            self._created_temp_dir.cleanup()

            self._created_temp_dir = None
            self._temp_path = None

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(file_path={self.original_path!r})"


class TempSourceDir(IsolatedTempDir):

    def load(self) -> None:
        with self._lock:
            if self.original_path.exists() is False:
                raise FileNotFoundError(f"Source Path {self.original_path.as_posix()!r} not found.")
            super().load()


class TempTargetDir(IsolatedTempDir):

    def apply_to_original_target(self) -> None:
        with self._lock:
            if self.closed is True:
                raise TempDirClosedError("Unable to apply to original target as the temp_dir is already closed.")
            if self.original_path.exists() is True:
                shutil.rmtree(self.original_path)
            self.original_path.mkdir(exist_ok=True, parents=True)
            shutil.copytree(self.temp_path, self.original_path, dirs_exist_ok=True)

    def load(self) -> None:
        with self._lock:
            # if self.original_path.exists() is True:
            #     super().load()
            pass


class IsolatedBuildEnvironment:

    def __init__(self, source_dir: Union[str, os.PathLike], target_dir: Union[str, os.PathLike]) -> None:
        self.source = TempSourceDir(source_dir)
        self.target = TempTargetDir(target_dir)
        os.environ["ORIGINAL_DOC_SOURCE_DIR"] = str(self.source.original_path)
        os.environ["ORIGINAL_DOC_TARGET_DIR"] = str(self.target.original_path)
        print(f"initialized {self}")

    def __enter__(self) -> "IsolatedBuildEnvironment":
        self.source.load()
        self.target.load()
        return self

    def __exit__(self,
                 exc_type: Optional[type[BaseException]],
                 exc_value: Optional[BaseException],
                 trace_back: Optional[TracebackType]):
        if exc_value is None:
            self.target.apply_to_original_target()

        self.source.cleanup()
        self.target.cleanup()
        if exc_value is not None:
            raise exc_value

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(source_dir={self.source.original_path.as_posix()!r}, target_dir={self.target.original_path.as_posix()!r})"
        # region [Main_Exec]


if __name__ == '__main__':
    pass

# endregion [Main_Exec]
