from invoke import task, Result, Context, Collection
from pathlib import Path


THIS_FILE_DIR = Path(__file__).parent.absolute()

PYPROJECT_TOML_FILE = THIS_FILE_DIR.joinpath("pyproject.toml")


VENV_FOLDER = THIS_FILE_DIR.joinpath('.venv')
SCRIPTS_FOLDER = VENV_FOLDER.joinpath('scripts')
VENV_ACTIVATOR_PATH = SCRIPTS_FOLDER.joinpath("activate.bat")


def activator_run(c: Context, command, echo=True, **kwargs) -> Result:
    with c.prefix(str(VENV_ACTIVATOR_PATH.resolve())):
        result = c.run(command, echo=echo, **kwargs)
        return result


@task
def compile_reqs(c):
    pip_compile_exe = f'"{SCRIPTS_FOLDER.joinpath("pip-compile.exe").resolve()!s}"'
    output_file = THIS_FILE_DIR.joinpath("compiled_reqs.txt")
    output_file.unlink(missing_ok=True)
    options = ["--no-header", "--no-annotate", "-r", f'-o {output_file.name!s}']
    arguments = [f'"{PYPROJECT_TOML_FILE!s}"']

    full_command = pip_compile_exe + ' ' + ' '.join(options) + ' ' + ' '.join(arguments)
    activator_run(c, full_command)

    text = output_file.read_text(encoding='utf-8', errors='ignore')
    new_lines = []
    for line in text.splitlines():
        new_lines.append(f'"{line}"')

    output_file.write_text(',\n'.join(new_lines), encoding='utf-8', errors='ignore')
