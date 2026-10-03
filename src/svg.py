from pathlib import Path
import xml.etree.ElementTree as ET

from models import GitHubStats


SVG_NAMESPACE = "http://www.w3.org/2000/svg"

ET.register_namespace("", SVG_NAMESPACE)


def render_svg(template_path: str | Path, output_path: str | Path, stats: GitHubStats,):
    tree = ET.parse(template_path)
    root = tree.getroot()
    elements = {
        element.get("id"): element
        for element in root.iter()
        if element.get("id")
    }
    update_dots(elements, "age_data_dots", "age_data", stats.age)
    update_dots(elements, "repo_data_dots", "repo_data", str(stats.repositories))
    update_dots(elements, "contrib_data_dots", "contrib_data", f"{stats.contributions:,}")
    update_dots(elements, "commit_data_dots", "commit_data", f"{stats.commits:,}")
    update_dots(elements, "pr_data_dots", "pr_data", f"{stats.pull_requests:,}")
    update_dots(elements, "star_data_dots", "star_data", str(stats.stars))
    update_dots(elements, "follower_data_dots", "follower_data", str(stats.followers))
    update_dots(elements, "loc_data_dots", "loc_data", f"{stats.loc:,}")
    elements["loc_add"].text = f"{stats.additions:,}"
    elements["loc_del"].text = f"{stats.deletions:,}"
    tree.write(
        output_path,
        encoding="UTF-8",
        xml_declaration=True,
    )


def update_dots(elements: dict, dots_id: str, value_id: str, value: str):
    dots_element = elements[dots_id]
    value_element = elements[value_id]
    original_dots = dots_element.text or ""
    original_value = value_element.text or ""
    field_width = (original_dots.count(".") + len(original_value))
    new_dot_count = max(1, field_width - len(value))
    dots_element.text = " " + "." * new_dot_count + " "
    value_element.text = value


def render_stats_svgs(stats: GitHubStats, template_dir: str | Path, output_dir: str | Path):
    template_dir = Path(template_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    render_svg(template_dir / "dark-mode.svg", output_dir / "dark-mode.svg", stats)
    render_svg(template_dir / "light-mode.svg", output_dir / "light-mode.svg", stats)