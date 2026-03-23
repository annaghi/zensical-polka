"""
Zensical hooks.

Replaces Zensical's built-in Markdown rendering with polka's
attribute-aware HTML output.
"""

import sys
from pathlib import Path

import zensical.main as main_module
import zensical.markdown as markdown_module
from zensical.config import get_config
from zensical.markdown import render as markdown_render

from bridge import generate_html


def main():
    """Patch Zensical's Markdown renderer and run the CLI."""
    is_clean_build = "--clean" in sys.argv or "-c" in sys.argv
    markdown_module.render = wrap_markdown(markdown_render, is_clean_build)
    main_module.cli()


def wrap_markdown(func, is_clean_build):
    """
    Wrap Zensical Markdown render function to use polka's HTML output.

    Calls the original render function to preserve metadata (e.g. TOC,
    frontmatter), then replaces the content with polka's HTML.
    """

    def wrapper(content: str, path: str, url: str) -> dict:
        config = get_config()
        result = func(content, path, url)

        result["meta"]["is_clean_build"] = is_clean_build

        icon_dirs = []
        custom_dir = config["theme"]["custom_dir"]
        if custom_dir:
            custom_icon_dir_candidate = Path(custom_dir) / ".icons"
            if custom_icon_dir_candidate.exists():
                icon_dirs.append(str(custom_icon_dir_candidate))

        html = generate_html(path.removesuffix(".md"), content, icon_dirs)

        result["content"] = html

        return result

    return wrapper


if __name__ == "__main__":
    main()
