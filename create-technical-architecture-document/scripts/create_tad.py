#!/usr/bin/env python3
"""Create a Markdown or multi-file AsciiDoc Technical Architecture Document."""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from datetime import date
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = SKILL_DIR / "assets"
DEFAULT_MODEL_VERSION = "c1787cdf061bdb9280116fa619e64879b01cbbcf"


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "system"


def replace_tokens(text: str, values: dict[str, str]) -> str:
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", value)
    return text


def refuse_dangerous_directory(target: Path, source: Path) -> None:
    resolved = target.resolve()
    source_resolved = source.resolve()
    cwd = Path.cwd().resolve()
    anchor = Path(resolved.anchor).resolve()

    if resolved in {anchor, cwd, SKILL_DIR.resolve(), ASSETS_DIR.resolve(), source_resolved}:
        raise ValueError(f"Refusing to replace unsafe directory: {resolved}")
    if resolved in source_resolved.parents:
        raise ValueError(f"Refusing to replace an ancestor of the template source: {resolved}")


def prepare_target(target: Path, force: bool, expect_directory: bool, source: Path | None = None) -> None:
    if not target.exists():
        return
    if not force:
        raise FileExistsError(f"Output already exists: {target}. Pass --force to replace it.")

    if expect_directory:
        if source is None:
            raise ValueError("Directory replacement requires a source safety boundary.")
        refuse_dangerous_directory(target, source)
        if target.is_dir():
            shutil.rmtree(target)
        else:
            target.unlink()
    else:
        if target.is_dir():
            raise IsADirectoryError(f"Markdown output must be a file, not a directory: {target}")
        target.unlink()


def create_markdown(args: argparse.Namespace, values: dict[str, str]) -> Path:
    template_name = (
        "technical-architecture-document-lean.md"
        if args.profile == "lean"
        else "technical-architecture-document.md"
    )
    source = ASSETS_DIR / template_name
    if not source.is_file():
        raise FileNotFoundError(f"Bundled template is missing: {source}")

    target = args.output or Path.cwd() / f"{slugify(args.project)}-technical-architecture.md"
    target = target.expanduser()
    prepare_target(target, args.force, expect_directory=False)
    target.parent.mkdir(parents=True, exist_ok=True)
    content = replace_tokens(source.read_text(encoding="utf-8"), values)
    target.write_text(content, encoding="utf-8", newline="\n")
    return target.resolve()


def initialize_asciidoc_readme(readme: Path, values: dict[str, str]) -> None:
    content = readme.read_text(encoding="utf-8")
    content = content.replace("# Architecture document", f"# {values['PROJECT_NAME']} Technical Architecture Document", 1)
    content = re.sub(
        r"(?m)^Model version\s*:\s*.*$",
        f"Model version : {values['MODEL_VERSION']}",
        content,
        count=1,
    )
    content = re.sub(
        r"(?m)^(?:##\s+)?\*Status\*:\s*.*$",
        f"*Status*: {values['STATUS']}",
        content,
        count=1,
    )
    metadata = (
        f"\nOwner: {values['OWNER']}  \n"
        f"Source revision: {values['SOURCE_REVISION']}  \n"
        f"Initialized: {values['DATE']}\n"
    )
    status_line = f"*Status*: {values['STATUS']}"
    content = content.replace(status_line, status_line + metadata, 1)
    readme.write_text(content, encoding="utf-8", newline="\n")


def create_asciidoc(args: argparse.Namespace, values: dict[str, str]) -> Path:
    source = ASSETS_DIR / "upstream-blank-asciidoc"
    if not source.is_dir():
        raise FileNotFoundError(f"Bundled AsciiDoc template is missing: {source}")

    target = args.output or Path.cwd() / f"{slugify(args.project)}-architecture"
    target = target.expanduser()
    prepare_target(target, args.force, expect_directory=True, source=source)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, target)
    initialize_asciidoc_readme(target / "README.adoc", values)
    return target.resolve()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a Technical Architecture Document from bundled templates."
    )
    parser.add_argument("--project", required=True, help="Project or system name.")
    parser.add_argument("--owner", default="TBD", help="Document owner or owning role.")
    parser.add_argument("--status", default="Draft", help="Initial document status.")
    parser.add_argument(
        "--source-revision",
        default="TBD",
        help="System/repository revision represented by the document.",
    )
    parser.add_argument(
        "--model-version",
        default=DEFAULT_MODEL_VERSION,
        help="Architecture template revision to record.",
    )
    parser.add_argument("--date", default=date.today().isoformat(), help="Initialization date (YYYY-MM-DD).")
    parser.add_argument(
        "--format",
        choices=("markdown", "asciidoc"),
        default="markdown",
        help="Output format. AsciiDoc creates a directory of views.",
    )
    parser.add_argument(
        "--profile",
        choices=("detailed", "lean"),
        default="detailed",
        help="Markdown template depth; ignored for AsciiDoc.",
    )
    parser.add_argument("--output", type=Path, help="Output file (Markdown) or directory (AsciiDoc).")
    parser.add_argument("--force", action="store_true", help="Explicitly replace existing output.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    values = {
        "PROJECT_NAME": args.project.strip(),
        "OWNER": args.owner.strip(),
        "STATUS": args.status.strip(),
        "DATE": args.date.strip(),
        "SOURCE_REVISION": args.source_revision.strip(),
        "MODEL_VERSION": args.model_version.strip(),
    }
    if not values["PROJECT_NAME"]:
        print("error: --project must not be blank", file=sys.stderr)
        return 2

    try:
        target = (
            create_asciidoc(args, values)
            if args.format == "asciidoc"
            else create_markdown(args, values)
        )
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"Created {args.format} Technical Architecture Document at: {target}")
    if args.format == "asciidoc":
        print("Keep ATTRIBUTION.md and LICENSE.md when redistributing the reusable template.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
