
# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import os
from pathlib import Path

# * Third Party Imports --------------------------------------------------------------------------------->
import click
from rich.table import Table
from sphinx.cmd.build import main as sphinx_build

# * Local Imports --------------------------------------------------------------------------------------->
from antistasi_sqf_tools import CONSOLE
from antistasi_sqf_tools.doc_creating.creator import Creator
from antistasi_sqf_tools.doc_creating.config_handling import CONFIG_FILE_NAME, find_config_file
from antistasi_sqf_tools.utilities import main_dir_from_git
# endregion [Imports]


THIS_FILE_DIR = Path(__file__).parent.absolute()

CLI_FILE_PATH_TYPUS = click.Path(exists=True, file_okay=True, dir_okay=False, resolve_path=True, path_type=Path)

CLI_DIR_PATH_TYPUS = click.Path(exists=False, file_okay=False, dir_okay=True, resolve_path=True, path_type=Path)


def add_doc_sub_group(top_group: click.Group):
    @top_group.group(name="docs")
    @click.help_option("-h", "--help")
    def docs_cli():
        ...

    @docs_cli.command(name="list-added-env")
    @click.help_option("-h", "--help")
    def list_added_env():
        from antistasi_sqf_tools.doc_creating.env_handling import EnvManager
        env_manager = EnvManager()
        for cat, items in env_manager.all_env_names.items():
            table = Table(title=cat.verbose_name, title_style="bold bright_white")
            table.add_column("Name", style="gold3", header_style="bold italic cyan")
            table.add_column("Var Name", style="grey89", header_style="bold italic cyan")
            table.add_column("Description", style="grey89", header_style="bold italic magenta")

            for item in items:
                table.add_row(item.name, item.var_name, item.description)

            CONSOLE.print(table)

    @docs_cli.command(name="sphinx-build")
    @click.help_option("-h", "--help")
    @click.option("-M", "--Make", is_flag=True)
    @click.argument("builder", default="html", type=click.STRING)
    @click.argument("source_dir", default=None, type=click.STRING)
    @click.argument("build_dir", default=None, type=click.STRING)
    @click.argument("sphinx_options", nargs=-1)
    def wrapped_sphinx_build(make, builder=None, source_dir=None, build_dir=None, sphinx_options=tuple()):
        arguments = []
        if make:
            arguments.append("-M")

        builder = builder or "html"
        arguments.append(builder)

        source_dir = source_dir or os.getcwd()
        arguments.append(source_dir)

        build_dir = build_dir or os.path.join(os.getcwd(), "build")
        arguments.append(build_dir)

        arguments.extend(sphinx_options)

        sphinx_build(arguments)

    @docs_cli.command()
    @click.help_option("-h", "--help")
    @click.option("-c", "--config-file", type=CLI_FILE_PATH_TYPUS)
    @click.option("-b", "--builder", type=click.STRING)
    def build(config_file=None, builder=None):
        config_file = config_file or find_config_file(CONFIG_FILE_NAME)
        builder = builder or "html"
        creator = Creator(config_file=config_file, builder_name=builder.casefold())
        creator.build()
        CONSOLE.rule(style="bold bright_white")
        CONSOLE.rule(title="DONE", style="bold bright_green")
        CONSOLE.rule(style="bold bright_white")

    @docs_cli.command()
    @click.help_option("-h", "--help")
    @click.argument("source-folder", required=True, type=CLI_DIR_PATH_TYPUS)
    @click.argument("target-folder", required=True, type=CLI_DIR_PATH_TYPUS)
    @click.pass_context
    def setup(ctx: click.Context,
              source_folder: Path,
              target_folder: Path) -> None:

        ...
