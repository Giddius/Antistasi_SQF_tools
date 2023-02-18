"""
# Workshop Info Parser

## Dependencies

* beautifulsoup4
* rich
* requests

```shell
pip install -U beautifulsoup4 rich requests
```

## Command line

### Syntax:

```shell
python workshop_info_parser.py <workshop_ids>
```

### Example:

```shell
python -m workshop_info_parser 893339590 773131200 893346105
```


### Output Example


```shell
python -m workshop_info_parser -f json 463939057
```





```json
[
    {
        "id": "463939057",
        "url": "https://steamcommunity.com/workshop/filedetails/?id=463939057",
        "title": "ace",
        "preview_image_main_source": "https://steamuserimages-a.akamaihd.net/ugc/964230428541162652/F7DC4A5DD2A4896E2D572D7E9E085489426FC64B/?imw=268&imh=268&ima=fit&impolicy=Letterbox&imcolor=%23000000&letterbox=true", // small image on the right side
        "file_size": 203334615.04, // in bytes
        "posted": 1434656940.0, // unix timestamp
        "updated": 1664298000.0, // unix timestamp
        "required_items": [ // other mod dependencies
            {
                "id": "450814997",
                "name": "CBA_A3",
                "url": "https://steamcommunity.com/workshop/filedetails/?id=450814997"
            }
        ]
    }
]
```

"""

# region [Imports]


import re
import sys
from time import sleep
import random
from pathlib import Path

from typing import TYPE_CHECKING, Optional, Iterable
from enum import Enum, auto, unique
from datetime import datetime, timezone, timedelta
from functools import lru_cache
from bs4 import BeautifulSoup
import httpx

from rich.console import Console as RichConsole, Group as RenderGroup

import argparse
from rich.rule import Rule
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.text import Text as RenderText
from rich.tree import Tree
from rich.progress import track
from rich.syntax import Syntax
from rich import box
from rich import traceback as rich_traceback
if TYPE_CHECKING:
    ...

# endregion [Imports]


# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

CONSOLE = RichConsole(soft_wrap=False, file=sys.stdout)
rich_traceback.install(console=CONSOLE)
# endregion [Constants]


@unique
class OUTPUT_FORMAT(Enum):
    JSON = "json"
    HUMAN = "human"


MONTH_MAP = {"jan": 1,
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
             "dec": 12}


def convert_title(in_value: str) -> str:
    return in_value.strip().removeprefix("Steam Workshop::")


def convert_file_size(in_value: str) -> Optional[int]:
    raw_value = in_value.strip().replace(",", "", 1)
    value, unit = raw_value.split(" ", maxsplit=1)
    mult = 1
    if unit.casefold().strip() == "kb":
        mult = 2**10

    elif unit.casefold().strip() == "mb":
        mult = 2**20

    elif unit.casefold().strip() == "gb":
        mult = 2**30

    return float(value.strip()) * mult

    # return raw_value


STEAM_DATETIME_REGEX = re.compile(r"(?P<day>\d+)\s*(?P<month_name>\w+)\s*\,?\s*(?P<year>\d+)?\s*\@\s+(?P<hour>\d+)\s*\:\s*(?P<minute>\d+)\s*(?P<meridiem>\w\w)")


def convert_steam_datetime_string(in_value: str) -> Optional[float]:
    if match := STEAM_DATETIME_REGEX.match(in_value.strip()):

        day = int(match.group("day"))
        year = int(match.group("year")) if match.group("year") else datetime.now().year
        minute = int(match.group("minute"))

        month = MONTH_MAP[match.group("month_name").strip().casefold()]

        raw_hours = int(match.group("hour"))
        raw_meridiem = match.group("meridiem").strip().casefold()
        hour = 0
        if raw_meridiem == "pm" and raw_hours < 12:
            hour = 12 + raw_hours

        else:
            hour = raw_hours

        date_time = datetime(year=year, month=month, day=day, hour=hour, minute=minute, second=0, microsecond=0, tzinfo=timezone(timedelta(hours=-8), "Etc/GMT+8")).astimezone(timezone.utc)

        return date_time.timestamp()


CONVERT_MAP = {"title": convert_title,
               "file_size": convert_file_size,
               "posted": convert_steam_datetime_string,
               "updated": convert_steam_datetime_string}


def parse_workshop_item_info(in_raw_html: str, workshop_item_id: str) -> dict[str, object]:
    item_info = {"id": workshop_item_id,
                 "url": f"https://steamcommunity.com/workshop/filedetails/?id={workshop_item_id}"}

    soup = BeautifulSoup(in_raw_html, 'html.parser')
    raw_title = soup.title.string

    item_info["title"] = CONVERT_MAP["title"](raw_title)
    try:
        item_info["preview_image_main_source"] = soup.find("img", {"id": "previewImageMain"}).attrs["src"]
    except AttributeError:
        item_info["preview_image_main_source"] = None

    details_data = soup.findAll("div", {"class": "rightDetailsBlock"})[1]

    names_stack = []

    for detail_name in details_data.findAll("div", {"class": "detailsStatLeft"}):
        name = detail_name.text.strip().replace(" ", "_").casefold()
        names_stack.append(name)

    for key_name, detail_value in zip(names_stack, details_data.findAll("div", {"class": "detailsStatRight"}), strict=True):
        item_info[key_name] = CONVERT_MAP[key_name](detail_value.text.strip())

    item_info["required_items"] = []
    try:
        reqs = soup.find("div", {"id": "RequiredItems"})

        for i in reqs.find_all('a', href=True):
            link = i.get('href', None)
            req_id = link.rsplit("?id=", maxsplit=1)[-1].strip()

            item_info["required_items"].append(get_workshop_item_info(req_id))

    except (IndexError, AttributeError):
        pass

    return item_info


@lru_cache()
def get_workshop_item_info(workshop_item_id: str) -> dict[str, object]:

    response = httpx.get(f"https://steamcommunity.com/workshop/filedetails/?id={workshop_item_id}", timeout=10)
    response.raise_for_status()
    html_text = response.text

    return parse_workshop_item_info(html_text, workshop_item_id)


class CustomArgParser(argparse.ArgumentParser):

    def print_usage(self, file=None) -> None:
        if file is None:
            console = CONSOLE
        else:
            console = RichConsole(soft_wrap=False, file=file)
        text = "usage: " + self.format_usage().strip().replace(".py", "").removeprefix("usage: ")
        console.print("")
        console.print(Syntax(text, lexer="shell", theme="github-dark"))
        console.print("")

    def print_help(self, file=None):
        if file is None:
            console = CONSOLE
        else:
            console = RichConsole(soft_wrap=False, file=file)

        dep_install_replace = """
```shell
pip install -U beautifulsoup4 rich requests
```""".strip()

        console.print(Panel(Markdown(__doc__.replace(dep_install_replace, "").replace("python -m ", "").replace("python ", "").replace(".py", "")), style="white", box=box.HEAVY_EDGE))
        super().print_help(file=file)

    def exit(self, status=0, message=None):
        if message:
            RichConsole(soft_wrap=True, file=sys.stderr).print(message, style="red")
        sys.exit(status)


def create_parser() -> argparse.ArgumentParser:
    parser = CustomArgParser()
    parser.add_argument("-f", "--format", choices=['json', 'human'], default="human")
    parser.add_argument("steam_workshop_ids", type=str, nargs='+',
                        help="One or more Steam Workshop Ids, seperated by a space.")

    return parser


def bytes2human(n):
    # http://code.activestate.com/recipes/578019
    # >>> bytes2human(10000)
    # '9.8K'
    # >>> bytes2human(100001221)
    # '95.4M'
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return '%.1f%s' % (value, s)
    return "%sB" % n


def _output_json(data: Iterable[dict]):
    CONSOLE.print_json(data=data)


def _output_human(data: Iterable[dict]):

    def make_item_data_table(in_item_data: dict):
        column_names = ("id", "title", "url", "preview_image_main_source", "file_size", "posted", "updated")
        main_data_table = Table(highlight=True, header_style="bold white on rgb(10,25,50)")
        main_data_table.add_column("Name", no_wrap=True)
        main_data_table.add_column("Value", no_wrap=True, overflow="ignore")

        for col_name in column_names:
            if col_name not in in_item_data:
                main_data_table.add_row(col_name.replace("_main_source", "").replace("_", " ").title(), "-")

            elif col_name == "title":
                main_data_table.add_row(col_name.replace("_", " ").title(), f'[bold underline]{in_item_data[col_name]}[/bold underline]')

            elif col_name == "file_size":
                main_data_table.add_row(col_name.replace("_", " ").title(), bytes2human(in_item_data[col_name]))

            elif col_name == "posted" or col_name == "updated":
                main_data_table.add_row(col_name.replace("_", " ").title(), datetime.fromtimestamp(in_item_data[col_name], tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S %Z"))

            else:
                main_data_table.add_row(col_name.replace("_", " ").title(), str(in_item_data[col_name]))

        return main_data_table

    def make_require_items_tree(in_required_items: list[dict], tree: Tree = None):
        for item in in_required_items:
            sub_required_items = item.pop("required_items", [])
            branch = tree.add(make_item_data_table(item))
            make_require_items_tree(sub_required_items, branch)

    def _render_item(in_item_data: dict):
        required_items = in_item_data.pop("required_items", [])
        title = f'[bold]{str(in_item_data.get("id", ""))}[/bold]'
        data_table = make_item_data_table(in_item_data)

        if required_items:
            required_items_tree = Tree("", guide_style="bold blue")
            make_require_items_tree(required_items, required_items_tree)

            return Panel(RenderGroup(data_table, RenderText("\n"), Panel(required_items_tree, style="white on rgb(50,50,50)", title="[bold]Required Items[/bold]", title_align="left", box=box.ROUNDED)), style="on rgb(0,25,0)", title=title, title_align="left")
        else:
            return Panel(data_table, style="on rgb(0,25,0)", title=title, title_align="left")

    output_tree = Tree("[bold underline italic]Workshop Data[/bold underline italic]\n")
    for item in data:
        output_tree.add(RenderGroup(_render_item(item), RenderText("\n")))
    CONSOLE.print()
    CONSOLE.print(Rule(characters="- "))
    CONSOLE.print()

    CONSOLE.print(output_tree)
    CONSOLE.print()

    CONSOLE.print(Rule(characters="- "))


def main() -> None:
    parser = create_parser()
    arguments = parser.parse_args()

    output_format = OUTPUT_FORMAT(arguments.format)

    _out = []

    if output_format is OUTPUT_FORMAT.HUMAN:
        for idx, steam_workshop_id in track(enumerate(arguments.steam_workshop_ids), description="Processing...", total=len(arguments.steam_workshop_ids), console=CONSOLE):

            _out.append(get_workshop_item_info(workshop_item_id=steam_workshop_id))
            if idx != 0:
                sleep(random.random() / random.randint(1, 2))

        _output_human(_out)

    elif output_format is OUTPUT_FORMAT.JSON:
        for idx, steam_workshop_id in enumerate(arguments.steam_workshop_ids):

            _out.append(get_workshop_item_info(workshop_item_id=steam_workshop_id))
            if idx != 0:
                sleep(random.random() / random.randint(1, 2))

        _output_json(_out)


# region [Main_Exec]
if __name__ == '__main__':
    main()
# endregion [Main_Exec]
