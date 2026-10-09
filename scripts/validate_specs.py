"""Validates the modular AsciiDoc specification: includes, anchors and cross-references.

Usage: python scripts/validate_specs.py [project-root]

Checks
- every master file exists and each ``include::`` target exists,
- every chapter in ``docs/<folder>/`` is included by its master file,
- anchors (``[#FR-1.1]``) are unique and live in the folder that owns their kind,
- every reference (``<<FR-1.1>>``) points to an existing anchor,
- traceability: each TS references a requirement, each US a TS and a requirement.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# master file -> (chapter folder, anchor kinds defined there)
MASTERS: dict[str, tuple[str, tuple[str, ...]]] = {
    "specification-web.adoc": ("docs/specifications", ("FR", "NFR")),
    "tech-specification-web.adoc": ("docs/tech-specifications", ("TS",)),
    "backlog-web.adoc": ("docs/backlog", ("US",)),
    "release-notes.adoc": ("docs/release-notes", ()),
}

ID = r"(?:FR|NFR|TS|US)-\d+(?:\.\d+)*"
INCLUDE_RE = re.compile(r"^include::([^\[]+)\[", re.MULTILINE)
ANCHOR_RE = re.compile(rf"^\[#({ID})\]\s*$", re.MULTILINE)
REFERENCE_RE = re.compile(rf"<<({ID})(?:,[^>]*)?>>")


def _kind(identifier: str) -> str:
    return identifier.split("-", 1)[0]


def _sections(text: str) -> list[tuple[str, str]]:
    """Each anchor with the text up to the next anchor, in document order."""
    anchors = list(ANCHOR_RE.finditer(text))
    return [
        (
            match.group(1),
            text[match.end() : anchors[i + 1].start() if i + 1 < len(anchors) else len(text)],
        )
        for i, match in enumerate(anchors)
    ]


def validate(root: Path) -> list[str]:
    """Return all problems found below ``root``; an empty list means the specs are valid."""
    errors: list[str] = []
    anchors: dict[str, Path] = {}
    sections: dict[str, str] = {}
    texts: dict[Path, str] = {}

    for master_name, (folder, kinds) in MASTERS.items():
        master = root / master_name
        if not master.is_file():
            errors.append(f"{master_name}: master file is missing")
            continue
        included: set[Path] = set()
        for target in INCLUDE_RE.findall(master.read_text(encoding="utf-8")):
            path = root / target.strip()
            if not path.is_file():
                errors.append(f"{master_name}: include target not found: {target}")
                continue
            included.add(path.resolve())
        for chapter in sorted((root / folder).glob("*.adoc")):
            relative = chapter.relative_to(root)
            if chapter.resolve() not in included:
                errors.append(f"{relative}: not included by {master_name}")
            text = chapter.read_text(encoding="utf-8")
            texts[relative] = text
            for identifier, body in _sections(text):
                if identifier in anchors:
                    errors.append(
                        f"{relative}: duplicate anchor {identifier} (also in {anchors[identifier]})"
                    )
                    continue
                if _kind(identifier) not in kinds:
                    errors.append(f"{relative}: anchor {identifier} does not belong in {folder}")
                anchors[identifier] = relative
                sections[identifier] = body

    for relative, text in texts.items():
        for identifier in sorted(set(REFERENCE_RE.findall(text))):
            if identifier not in anchors:
                errors.append(f"{relative}: unresolved reference <<{identifier}>>")

    for identifier, body in sections.items():
        referenced = {_kind(reference) for reference in REFERENCE_RE.findall(body)}
        needs_requirement = _kind(identifier) in ("TS", "US")
        if needs_requirement and not referenced & {"FR", "NFR"}:
            errors.append(f"{anchors[identifier]}: {identifier} references no requirement")
        if _kind(identifier) == "US" and "TS" not in referenced:
            errors.append(
                f"{anchors[identifier]}: {identifier} references no technical specification"
            )
    return errors


def main(argv: list[str]) -> int:
    root = Path(argv[1]) if len(argv) > 1 else Path(__file__).resolve().parent.parent
    errors = validate(root)
    for error in errors:
        sys.stderr.write(f"{error}\n")
    if errors:
        sys.stderr.write(f"{len(errors)} problem(s) found\n")
        return 1
    sys.stdout.write("specifications are valid\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
