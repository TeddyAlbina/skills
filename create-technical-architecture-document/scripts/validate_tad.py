#!/usr/bin/env python3
"""Validate the structure and hygiene of a Technical Architecture Document."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    message: str


LEAN_SECTIONS = {
    "summary": ("summary", "executive summary"),
    "scope": ("scope", "purpose"),
    "context": ("context", "target architecture", "architecture overview"),
    "constraints": ("constraint", "driver"),
    "quality requirements": ("quality", "non-functional", "nfr"),
    "application view": ("application",),
    "development view": ("development", "software"),
    "infrastructure view": ("infrastructure", "deployment"),
    "security view": ("security",),
    "sizing view": ("sizing", "capacity", "performance"),
    "decisions": ("decision", "adr"),
    "risks": ("risk",),
    "language/glossary": ("ubiquitous language", "glossary", "terminology"),
    "evidence/references": ("evidence", "reference"),
}

STANDARD_ADDITIONS = {
    "document control": ("document control", "revision history"),
    "stakeholders": ("stakeholder", "audience"),
    "assumptions/unresolved": ("assumption", "unresolved", "not ruled"),
    "transition": ("transition", "migration", "roadmap"),
    "traceability": ("traceability", "consistency"),
}

STRICT_ADDITIONS = {
    "interfaces/data flows": ("interface", "data flow", "critical flow"),
    "recovery": ("recovery", "backup", "restore", "rto", "rpo"),
    "observability/operations": ("observability", "monitoring", "operations"),
    "trust/security boundary": ("trust", "threat"),
    "capacity calculations": ("capacity calculation", "workload model", "sizing"),
    "verification/testing": ("verification", "test strategy", "validation"),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a Markdown or AsciiDoc TAD.")
    parser.add_argument("path", type=Path, help="Document file or directory containing Markdown/AsciiDoc views.")
    parser.add_argument(
        "--profile",
        choices=("lean", "standard", "strict"),
        default="standard",
        help="Required depth.",
    )
    parser.add_argument(
        "--allow-placeholders",
        action="store_true",
        help="Do not warn about template placeholders or unowned TBD markers.",
    )
    parser.add_argument("--fail-on-warnings", action="store_true", help="Return non-zero when warnings exist.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    return parser.parse_args()


def load_document(path: Path) -> tuple[str, list[str]]:
    if path.is_file():
        if path.suffix.lower() not in {".md", ".adoc", ".asciidoc"}:
            raise ValueError("Expected a .md, .adoc, or .asciidoc file.")
        return path.read_text(encoding="utf-8"), [str(path.resolve())]

    if not path.is_dir():
        raise FileNotFoundError(f"Document path does not exist: {path}")

    excluded = {"license.md", "attribution.md"}
    files = sorted(
        item
        for item in path.rglob("*")
        if item.is_file()
        and item.suffix.lower() in {".md", ".adoc", ".asciidoc"}
        and item.name.lower() not in excluded
    )
    if not files:
        raise ValueError(f"No Markdown or AsciiDoc files found under: {path}")
    chunks = [f"\n\n<!-- SOURCE: {item} -->\n\n{item.read_text(encoding='utf-8')}" for item in files]
    return "".join(chunks), [str(item.resolve()) for item in files]


def extract_headings(text: str) -> list[str]:
    headings: list[str] = []
    pattern = re.compile(r"(?m)^(?:#{1,6}|={1,6})\s+(.+?)\s*$")
    for match in pattern.finditer(text):
        heading = re.sub(r"[*_`#]", "", match.group(1)).strip().lower()
        headings.append(heading)
    return headings


def has_heading(headings: list[str], alternatives: tuple[str, ...]) -> bool:
    return any(term in heading for heading in headings for term in alternatives)


def required_sections(profile: str) -> dict[str, tuple[str, ...]]:
    required = dict(LEAN_SECTIONS)
    if profile in {"standard", "strict"}:
        required.update(STANDARD_ADDITIONS)
    if profile == "strict":
        required.update(STRICT_ADDITIONS)
    return required


def strip_comments_and_code(text: str) -> str:
    without_comments = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    return re.sub(r"```.*?```", "", without_comments, flags=re.DOTALL)


def count_diagrams(text: str) -> int:
    mermaid = len(re.findall(r"(?im)^```mermaid\s*$", text))
    plantuml = len(re.findall(r"(?im)(?:^```plantuml\s*$|^@startuml\s*$)", text))
    image_refs = len(re.findall(r"(?im)(?:^image::?[^\[]+\[|!\[[^\]]*\]\([^\)]+\))", text))
    return mermaid + plantuml + image_refs


def validate(text: str, profile: str, allow_placeholders: bool) -> list[Finding]:
    findings: list[Finding] = []
    headings = extract_headings(text)

    for label, alternatives in required_sections(profile).items():
        if not has_heading(headings, alternatives):
            findings.append(Finding("error", "missing-section", f"Missing required section: {label}."))

    diagrams = count_diagrams(text)
    minimum_diagrams = {"lean": 1, "standard": 2, "strict": 3}[profile]
    if diagrams < minimum_diagrams:
        severity = "error" if profile == "strict" else "warning"
        findings.append(
            Finding(
                severity,
                "diagram-depth",
                f"Found {diagrams} diagram reference(s); profile {profile} expects at least {minimum_diagrams}.",
            )
        )

    nfr_ids = set(re.findall(r"\bNFR-[A-Z0-9-]+", text, flags=re.IGNORECASE))
    if not nfr_ids:
        findings.append(Finding("error", "missing-nfr-ids", "No stable NFR identifiers were found."))

    measurable_lines = [
        line
        for line in text.splitlines()
        if re.search(r"\bNFR-[A-Z0-9-]+", line, flags=re.IGNORECASE)
        and re.search(
            r"(?:\d+(?:\.\d+)?\s*(?:%|ms|s|sec|seconds?|min|minutes?|h|hours?|rps|tps|/s|gib|mib|gb|tb|days?|years?)|p9[059]|rto|rpo)",
            line,
            flags=re.IGNORECASE,
        )
    ]
    if nfr_ids and not measurable_lines:
        severity = "error" if profile == "strict" else "warning"
        findings.append(
            Finding(severity, "unmeasured-nfr", "NFR IDs exist, but no NFR row contains an obvious numeric measure/unit.")
        )

    adr_ids = set(re.findall(r"\bADR-\d+", text, flags=re.IGNORECASE))
    if profile in {"standard", "strict"} and not adr_ids:
        findings.append(Finding("warning", "missing-adr-links", "No ADR identifiers were found."))

    trace_ids = set(re.findall(r"\b(?:CON|DRV|NFR|ADR|RISK|TBD)-[A-Z0-9-]+", text, flags=re.IGNORECASE))
    if profile in {"standard", "strict"} and len(trace_ids) < 4:
        findings.append(
            Finding("warning", "weak-traceability", f"Only {len(trace_ids)} stable traceability ID(s) were found.")
        )

    if not allow_placeholders:
        inspectable = strip_comments_and_code(text)
        token_placeholders = re.findall(r"{{[A-Z0-9_ -]+}}", inspectable)
        angle_placeholders = re.findall(r"<[^>\n]{2,80}>", inspectable)
        placeholder_count = len(token_placeholders) + len(angle_placeholders)
        if placeholder_count:
            findings.append(
                Finding(
                    "warning",
                    "placeholders",
                    f"Found {placeholder_count} unresolved template placeholder(s).",
                )
            )

        unowned_tbd = [
            line.strip()
            for line in inspectable.splitlines()
            if re.search(r"\bTBD\b", line, flags=re.IGNORECASE)
            and not re.search(r"owner|due|\|", line, flags=re.IGNORECASE)
        ]
        if unowned_tbd:
            findings.append(
                Finding(
                    "warning",
                    "unowned-tbd",
                    f"Found {len(unowned_tbd)} TBD line(s) without an obvious owner/due-date field.",
                )
            )

    secret_assignment = re.compile(
        r"(?im)\b(?:password|passwd|api[_ -]?key|client[_ -]?secret|private[_ -]?key|access[_ -]?token)\s*[:=]\s*['\"]?[A-Za-z0-9+/_.-]{8,}"
    )
    if secret_assignment.search(text):
        findings.append(
            Finding("error", "possible-secret", "Found a possible credential/secret assignment; remove sensitive values.")
        )

    private_ip = re.compile(
        r"\b(?:10(?:\.\d{1,3}){3}|192\.168(?:\.\d{1,3}){2}|172\.(?:1[6-9]|2\d|3[01])(?:\.\d{1,3}){2})\b"
    )
    if private_ip.search(text):
        findings.append(
            Finding("warning", "private-address", "Found private IPv4 addressing; prefer linked operational inventory unless essential.")
        )

    unresolved_heading = has_heading(headings, ("unresolved", "not ruled"))
    if unresolved_heading and not re.search(r"(?im)^\|[^\n]*owner[^\n]*(?:due|date)", text):
        findings.append(
            Finding("warning", "unowned-unresolved", "Unresolved points exist without an obvious Owner and Due/Date table header.")
        )

    return findings


def main() -> int:
    args = parse_args()
    try:
        text, files = load_document(args.path.expanduser())
        findings = validate(text, args.profile, args.allow_placeholders)
    except (OSError, UnicodeError, ValueError) as exc:
        if args.json:
            print(json.dumps({"ok": False, "error": str(exc)}, indent=2))
        else:
            print(f"error: {exc}", file=sys.stderr)
        return 2

    errors = sum(item.severity == "error" for item in findings)
    warnings = sum(item.severity == "warning" for item in findings)
    ok = errors == 0 and (not args.fail_on_warnings or warnings == 0)

    if args.json:
        print(
            json.dumps(
                {
                    "ok": ok,
                    "profile": args.profile,
                    "files": files,
                    "summary": {"errors": errors, "warnings": warnings},
                    "findings": [asdict(item) for item in findings],
                },
                indent=2,
            )
        )
    else:
        print(f"Validated {len(files)} file(s) with profile '{args.profile}'.")
        for item in findings:
            print(f"{item.severity.upper():7} {item.code}: {item.message}")
        print(f"Result: {errors} error(s), {warnings} warning(s).")

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
