import pytest
from pathlib import Path


@pytest.fixture
def fake_source_dir(tmp_path: Path):
    source_dir = tmp_path.joinpath("source")
    source_dir.mkdir(exist_ok=True, parents=True)
    return source_dir


@pytest.fixture
def non_existing_source_dir(tmp_path: Path):
    source_dir = tmp_path.joinpath("non_existing_source")
    return source_dir


@pytest.fixture
def source_dir_with_file(tmp_path: Path):
    source_dir = tmp_path.joinpath("source")
    source_dir.mkdir(exist_ok=True, parents=True)
    source_dir.joinpath("a_file.txt").touch(exist_ok=True)
    return source_dir


@pytest.fixture
def fake_target_dir(tmp_path: Path):
    target_dir = tmp_path.joinpath("created")
    target_dir.mkdir(exist_ok=True, parents=True)
    return target_dir


@pytest.fixture
def non_existing_target_dir(tmp_path: Path):
    target_dir = tmp_path.joinpath("non_existing_created")
    return target_dir


@pytest.fixture
def target_dir_with_file(tmp_path: Path):
    target_dir = tmp_path.joinpath("created")
    target_dir.mkdir(exist_ok=True, parents=True)
    target_dir.joinpath("a_file.txt").touch(exist_ok=True)
    return target_dir
