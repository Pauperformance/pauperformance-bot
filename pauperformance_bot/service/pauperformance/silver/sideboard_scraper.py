import csv
import io
import os
import re

import requests

from pauperformance_bot.constant.pauperformance.myr import MyrFileSystem
from pauperformance_bot.constant.pauperformance.silver import SIDEBOARD_GUIDE_SHEET_URL
from pauperformance_bot.entity.config.archetype import SideboardResource
from pauperformance_bot.util.log import get_application_logger

logger = get_application_logger()

_ARCHETYPE_MAP = {
    "Mono Blue Terror": "MonoU Terror",
    "Mono Red Madness": "MonoR Madness",
    "Grixis Affinity": "Affinity",
    "Spy Combo": "Spy Walls",
    "Mono Blue Faeries": "MonoU Faeries",
    "Cawgates": "Azorius Gates",
    "Black Sac": "MonoB Sacrifice",
    "Azorius Familiars": "Familiars",
    "Gruul Monsters": "Gruul Ramp",
    "Dredge": "Golgari Dredge",
    "Mono White Heroic": "MonoW Heroic",
    "Walls Combo": "Walls",
    "Cycle Storm": "Cycling Storm",
    "High Tide": "MonoU High Tide",
}


def _to_csv_export_url(sheet_url: str) -> str:
    sheet_id = re.search(r"/spreadsheets/d/([^/]+)/", sheet_url).group(1)
    gid_match = re.search(r"[?&#]gid=(\d+)", sheet_url)
    gid = gid_match.group(1) if gid_match else "0"
    base = sheet_url.split("/spreadsheets/")[0]
    return f"{base}/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"


def _download_sideboard_guides() -> dict[str, list[SideboardResource]]:
    csv_url = _to_csv_export_url(SIDEBOARD_GUIDE_SHEET_URL)
    response = requests.get(csv_url)
    response.raise_for_status()
    reader = csv.reader(io.StringIO(response.content.decode("utf-8")))
    next(reader)  # skip header row
    guides: dict[str, list[SideboardResource]] = {}
    for row in reader:
        if not row or not row[0].strip():
            continue
        archetype_name = row[0].strip()
        row_guides = []
        # columns after the first are groups of 4: Author, Guide, Price, Notes
        for offset in range(1, len(row), 4):
            author, link, price, notes = (row[offset : offset + 4] + ["", "", "", ""])[
                :4
            ]
            author = (
                author.replace("Kalikaiz", "saidin.raken")
                .replace("Skura", "FSkura")
                .replace("Ziofrancone", "ziofrancone")
                .replace("Othesemo", "othesemo")
                .replace("Wolf777", "wolf777")
                .replace("Wolf777", "wolf777")
                .replace("Barff", "barff")
                .replace("Alessandro Piraccini", "AlessandroPiraccini")
                .replace("Sodek", "Sodeq")
                .replace("Pietrol10, Edo_01, MVanni & ciurlo", "ciurlo")
                .replace("AllEyezOnMe", "Alleyezonme")
                .replace("Gustavo Parra", "PedraStone")
                .replace("SpockVidaLoca", "SpockVidaLoca")
                .replace("Bryant Cook", "Bryant_Cook")
            )
            if not link.strip():
                break
            row_guides.append(
                SideboardResource(
                    author=author.strip(),
                    link=link.strip(),
                    price=price.strip(),
                    notes=notes.strip() or None,
                )
            )
        if row_guides:
            guides.setdefault(
                _ARCHETYPE_MAP.get(archetype_name, archetype_name), []
            ).extend(row_guides)
    return guides


def _format_sideboard_section(i: int, guide: SideboardResource) -> str:
    return (
        f"[sideboard{i}]\n"
        f"author = {guide.author}\n"
        f"url = {guide.link}\n"
        f"price = {guide.price}\n"
        f"notes = {guide.notes or ''}\n"
    )


def _extract_sideboard_sections(text: str) -> list[str]:
    return re.findall(r"\[sideboard\d+\][^\[]*", text)


def _url_from_section(section_text: str) -> str:
    match = re.search(r"^url\s*=\s*(.+)$", section_text, re.MULTILINE)
    return match.group(1).strip() if match else ""


def _renumber_sideboard_section(section_text: str, new_index: int) -> str:
    return re.sub(r"\[sideboard\d+\]", f"[sideboard{new_index}]", section_text, count=1)


def update_sideboard_guides():
    guides: dict[str, list[SideboardResource]] = _download_sideboard_guides()
    archetypes_dir = MyrFileSystem().RESOURCES_CONFIG_ARCHETYPES_DIR
    for archetype_name, archetype_guides in guides.items():
        config_path = os.path.join(archetypes_dir, f"{archetype_name}.ini")
        if not os.path.exists(config_path):
            logger.warning(
                f"Config file not found for archetype '{archetype_name}': {config_path}"
            )
            continue
        with open(config_path) as f:
            text = f.read()

        # Preserve manually added sections whose URL is not in the sheet
        sheet_urls = {guide.link for guide in archetype_guides}
        manual_sections = [
            s
            for s in _extract_sideboard_sections(text)
            if _url_from_section(s) not in sheet_urls
        ]

        # Remove all existing [sideboardN] sections
        text = re.sub(r"\[sideboard\d+\][^\[]*", "", text)

        # Sheet sections first, then manual ones; renumber the whole sequence
        sheet_parts = [
            _format_sideboard_section(i, guide)
            for i, guide in enumerate(archetype_guides, 1)
        ]
        offset = len(archetype_guides) + 1
        manual_parts = [
            _renumber_sideboard_section(s, offset + j)
            for j, s in enumerate(manual_sections)
        ]
        new_sections = "\n".join(sheet_parts + manual_parts)

        # Insert before [discord] or [resource] sections; append if neither exists
        insert_match = re.search(r"\[(discord|resource)\d+\]", text)
        if insert_match:
            pos = insert_match.start()
            text = text[:pos] + new_sections + "\n\n" + text[pos:]
        else:
            text = text.rstrip("\n") + "\n\n" + new_sections + "\n"

        with open(config_path, "w") as f:
            f.write(text)
        logger.info(f"Updated sideboard guides for '{archetype_name}'.")
