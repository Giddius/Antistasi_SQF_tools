from pathlib import Path


TEMPLATES_DIR = Path(__file__).parent.absolute()


PLACEHOLDER_LOGO_FILE = TEMPLATES_DIR.joinpath("placeholder_logo.png")
PLACEHOLDER_FAVICON_FILE = TEMPLATES_DIR.joinpath("placeholder_favicon.png")
