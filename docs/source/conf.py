
# region [Imports]

import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.abspath('.'))


import antistasi_sqf_tools


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    ...


# endregion [Imports]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

ORIGINAL_SOURCE_DIR = Path(os.getenv("ORIGINAL_DOC_SOURCE_DIR", None)).resolve() if os.getenv("ORIGINAL_DOC_SOURCE_DIR", None) is not None else THIS_FILE_DIR
ORIGINAL_TARGET_DIR = Path(os.getenv("ORIGINAL_DOC_TARGET_DIR", None)).resolve() if os.getenv("ORIGINAL_DOC_TARGET_DIR", None) is not None else THIS_FILE_DIR.parent.joinpath("docs")

# endregion [Constants]

# region [Project_Info]

project = 'Antistasi Sqf Tools'
copyright = 'Antistasi Tools'
author = 'Antistasi Tools'
release = antistasi_sqf_tools.__version__


html_logo = "_images/app_logo.png"
html_favicon = "_images/app_favicon.png"


# endregion [Project_Info]

# region [Sphinx_Settings]

extensions = ['sphinxcontrib.mermaid',
              'sphinx_inline_tabs',
              'sphinx.ext.githubpages',
              'sphinx_copybutton',
              'sphinx_design',
              'sphinx.ext.autosectionlabel',
              'sphinx_issues',
              'sphinx.ext.graphviz',
              'antistasi_sqf_tools.doc_creating.sphinx_extensions']

templates_path = ['_templates']

html_static_path = ['_static']
html_css_files = [
    'css/extra_styling.css'
]

exclude_patterns = []


# get available styles via `pygmentize -L styles`
pygments_style = "monokai"


# endregion [Sphinx_Settings]

# region [Extension_Settings]

autosectionlabel_prefix_document = True


# endregion [Extension_Settings]

# region [HTML_Output_Settings]

html_copy_source = False
html_theme = 'furo'


html_context = {"base_css_name": html_theme}

rst_epilog = ""

html_theme_options = {"sidebarwidth": "100em",
                      "light_css_variables": {},
                      "dark_css_variables": {},
                      "source_repository": "https://github.com/Giddius/Antistasi_SQF_tools",
                      "source_branch": "main",
                      "source_directory": "docs/source/",
                      "footer_icons": [
                          {
                              "name": "GitHub",
                              "url": "https://github.com/Giddius/Antistasi_SQF_tools",
                              "html": """
                <svg stroke="currentColor" fill="currentColor" stroke-width="0" viewBox="0 0 16 16">
                    <path fill-rule="evenodd" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0 0 16 8c0-4.42-3.58-8-8-8z"></path>
                </svg>
            """,
                              "class": "",
                          },
                      ]}


html_title = f'{project}'

# endregion [HTML_Output_Settings]

# region [Setup]


# endregion [Setup]
