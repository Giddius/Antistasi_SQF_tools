from invoke import task, Result, Context, Collection

from gid_tasks.project_info.project import Project
from gid_tasks.hackler.imports_cleaner import import_clean_project
from pathlib import Path

THIS_FILE_DIR = Path(__file__).parent.absolute()


@task
def clean_imports(c: Context):
    project = Project()
    for _file in import_clean_project(project=project):
        print(f"cleaned {_file.as_posix()!r}", flush=True)
