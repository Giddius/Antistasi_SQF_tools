"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import sys
from typing import TYPE_CHECKING
from pathlib import Path

# * Third Party Imports --------------------------------------------------------------------------------->
import jinja2

if sys.version_info >= (3, 11):
    pass
else:
    pass
# * Type-Checking Imports --------------------------------------------------------------------------------->
if TYPE_CHECKING:
    from sphinx.application import Sphinx as SphinxApplication

    from .external_link_collection import FixedExternalLinkCollection

# endregion [Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion [Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion [Constants]

DEFAULT_TEMPLATE: str = """

Links
======


{% for category, links in data %}


{{ category.pretty_name }}
----------------------------------------------------------------

{% for link in links %}


:l:`{{ link.name }}`
    {{ link.description or  "..." }}

{% endfor %}

{% endfor %}
"""


SPHINX_DESIGN_DEFAULT_TEMPLATE = """

Links
======



{% for category, links in data %}

.. card:: {{ category.pretty_name }}
   :shadow: md


   {% for ext_link in links %}

   :l:`{{ ext_link.name }}`
      {{ ext_link.description or "..." }}


   {% endfor %}


{% endfor %}

"""


def build_link_file(app: "SphinxApplication", link_collection: "FixedExternalLinkCollection", template_name: str):
    with Path(app.srcdir).joinpath("links.rst").resolve().open("w", encoding='utf-8', errors='ignore') as f:
        try:
            f.write(app.builder.templates.render(template_name, {"data": link_collection.get_link_file_data()}))
        except jinja2.TemplateNotFound:
            template_string = DEFAULT_TEMPLATE
            if "sphinx_design" in app.config.extensions:
                template_string = SPHINX_DESIGN_DEFAULT_TEMPLATE
            f.write(app.builder.templates.render_string(template_string, {"data": link_collection.get_link_file_data()}))


# region [Main_Exec]
if __name__ == '__main__':
    pass
# endregion [Main_Exec]
