import pytest
from pytest import param
from antistasi_sqf_tools.doc_creating.isolated_build_env import TempSourceDir, TempTargetDir, IsolatedBuildEnvironment
from pathlib import Path
from pytest_lazyfixture import lazy_fixture
from antistasi_sqf_tools.errors import TempDirClosedError


@pytest.mark.parametrize("input_dir, result", [
    param(lazy_fixture("fake_source_dir"), {"exists": True, "name": "source", "files": []}),
    param(lazy_fixture("non_existing_source_dir"), {"exists": False, "name": "non_existing_source", "files": []}),
    param(lazy_fixture("source_dir_with_file"), {"exists": True, "name": "source", "files": ["a_file.txt"]}),

])
def test_temp_source_dir_init(input_dir: Path, result: dict[str, object]):
    assert input_dir.exists() is result["exists"]
    assert input_dir.name == result["name"]
    temp_source_dir = TempSourceDir(input_dir)
    assert set(i.name for i in temp_source_dir.temp_path.iterdir() if i.is_file()) == set()
    assert set(i.name for i in temp_source_dir.temp_path.iterdir() if i.is_dir()) == set()
    if result["exists"] is False:
        with pytest.raises(FileNotFoundError):
            temp_source_dir.load()

    else:
        temp_source_dir.load()

        assert set(i.name for i in temp_source_dir.temp_path.iterdir() if i.is_file()) == set(result["files"])

        assert temp_source_dir.temp_path.exists() is True
        assert temp_source_dir.closed is False

        temp_source_dir.cleanup()

        assert temp_source_dir.closed is True

        temp_source_dir.cleanup()


@pytest.mark.parametrize("input_dir, result", [
    param(lazy_fixture("fake_target_dir"), {"exists": True, "name": "created", "files": [], "folder":[]}),
    param(lazy_fixture("non_existing_target_dir"), {"exists": False, "name": "non_existing_created", "files": [], "folder":[]}),
    param(lazy_fixture("target_dir_with_file"), {"exists": True, "name": "created", "files": ["a_file.txt"], "folder":[]}),


])
def test_temp_target_dir_init(input_dir: Path, result: dict[str, object]):
    assert input_dir.exists() is result["exists"]
    assert input_dir.name == result["name"]

    temp_target_dir = TempTargetDir(input_dir)
    assert set(i.name for i in temp_target_dir.temp_path.iterdir() if i.is_file()) == set()
    assert set(i.name for i in temp_target_dir.temp_path.iterdir() if i.is_dir()) == set()
    temp_target_dir.load()

    assert set(i.name for i in temp_target_dir.temp_path.iterdir() if i.is_file()) == set(result["files"])
    assert set(i.name for i in temp_target_dir.temp_path.iterdir() if i.is_dir()) == set(result["folder"])
    assert temp_target_dir.temp_path.exists() is True
    assert temp_target_dir.closed is False

    added_file_1 = temp_target_dir.temp_path.joinpath("added_file_1.txt")
    added_file_1.touch()
    assert set(i.name for i in temp_target_dir.temp_path.iterdir() if i.is_file()) == set(result["files"] + [added_file_1.name])

    temp_target_dir.apply_to_original_target()

    assert input_dir.exists() is True

    assert set(i.name for i in input_dir.iterdir() if i.is_file()) == set(result["files"] + [added_file_1.name])

    temp_target_dir.cleanup()

    assert temp_target_dir.closed is True

    temp_target_dir.cleanup()

    with pytest.raises(TempDirClosedError):
        temp_target_dir.apply_to_original_target()
