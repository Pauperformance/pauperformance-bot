import os
from pathlib import Path
from urllib.parse import quote

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from pauperformance_bot.constant.pauperformance.academy import (
    RESOURCES_IMAGES_MANA_RELATIVE_URL,
)
from pauperformance_bot.util.log import get_application_logger
from pauperformance_bot.util.time import pretty_str, simple_str

logger = get_application_logger()


def tagify(name):
    return f"`{name}`"


def to_archetype_page_mana(mana):
    return (
        f'<img src="../{RESOURCES_IMAGES_MANA_RELATIVE_URL}/{mana}.png" '
        f'class="dominant-mana-icon"/>'
    )


def to_github_anchor(name):
    return name.lower().replace(" ", "-").replace(".", "").replace(":", "")


def to_url_encoded(name):
    return quote(name)


def render_template(template_dir, template_file, output_file, values):
    os.makedirs(Path(output_file).parent.as_posix(), exist_ok=True)
    env = Environment(
        loader=FileSystemLoader(template_dir),
        undefined=StrictUndefined,
    )
    env.filters["tagify"] = tagify
    env.filters["to_archetype_page_mana"] = to_archetype_page_mana
    rendered_file = env.get_template(template_file).render(
        values,
        pretty_str=pretty_str,
        simple_str=simple_str,
        to_github_anchor=to_github_anchor,
        to_url_encoded=to_url_encoded,
    )
    with open(output_file, "w") as out_f:
        logger.debug("Replacing template with rendered file rendered file...")
        out_f.write(rendered_file)
