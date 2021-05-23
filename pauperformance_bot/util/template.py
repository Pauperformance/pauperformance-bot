from jinja2 import Environment, FileSystemLoader, StrictUndefined
from pauperformance_bot.util.log import get_application_logger

logger = get_application_logger()


def tagify(name):
    return f"`{name}`"


def render_template(template_dir, template_file, output_file, values):
    env = Environment(
        loader=FileSystemLoader(template_dir),
        undefined=StrictUndefined,
    )
    env.filters['tagify'] = tagify
    rendered_file = env.get_template(template_file).render(values)
    with open(output_file, "w") as out_f:
        logger.debug(
            f"Replacing template with rendered file {rendered_file}..."
        )
        out_f.write(rendered_file)
