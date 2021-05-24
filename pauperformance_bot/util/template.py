from jinja2 import Environment, FileSystemLoader, StrictUndefined

from pauperformance_bot.constants import \
    PAUPERFORMANCE_RESOURCES_IMAGES_MANA_RELATIVE_URL
from pauperformance_bot.util.log import get_application_logger
from pauperformance_bot.util.time import pretty_str

logger = get_application_logger()


def tagify(name):
    return f"`{name}`"


def to_archetype_page_mana(mana):
    return f"<img src=\"../{PAUPERFORMANCE_RESOURCES_IMAGES_MANA_RELATIVE_URL}/{mana}.png\" width=\"25\"/>"


def render_template(template_dir, template_file, output_file, values):
    env = Environment(
        loader=FileSystemLoader(template_dir),
        undefined=StrictUndefined,
    )
    env.filters['tagify'] = tagify
    env.filters['to_archetype_page_mana'] = to_archetype_page_mana
    rendered_file = env.get_template(template_file).render(
        values,
        pretty_str=pretty_str,
    )
    with open(output_file, "w") as out_f:
        logger.debug(
            f"Replacing template with rendered file {rendered_file}..."
        )
        out_f.write(rendered_file)
