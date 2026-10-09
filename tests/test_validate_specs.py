"""The specification validator (NFR-2)."""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.validate_specs import main, validate
from wos_intel.config import PROJECT_ROOT

pytestmark = pytest.mark.integration

REQUIREMENT = "[#FR-1.1]\n=== Requirement\n\nText.\n"
TECH = "[#TS-1.1]\n=== Design\n\nImplements <<FR-1.1>>.\n"
STORY = "[#US-1.1]\n=== Story\n\nTraces to <<TS-1.1>> and <<FR-1.1,the requirement>>.\n"


def write_tree(
    root: Path, requirement: str = REQUIREMENT, tech: str = TECH, story: str = STORY
) -> None:
    chapters = {
        "specification-web.adoc": ("docs/specifications", requirement),
        "tech-specification-web.adoc": ("docs/tech-specifications", tech),
        "backlog-web.adoc": ("docs/backlog", story),
        "release-notes.adoc": ("docs/release-notes", "== 0.1.0\n\n<<FR-1.1>>\n"),
    }
    for master, (folder, content) in chapters.items():
        (root / folder).mkdir(parents=True, exist_ok=True)
        (root / folder / "01-chapter.adoc").write_text(content, encoding="utf-8")
        (root / master).write_text(f"= Master\n\ninclude::{folder}/01-chapter.adoc[]\n", "utf-8")


def test_project_specifications_are_valid() -> None:
    assert validate(PROJECT_ROOT) == []


def test_valid_tree(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    write_tree(tmp_path)

    assert validate(tmp_path) == []
    assert main(["validate_specs.py", str(tmp_path)]) == 0
    assert "valid" in capsys.readouterr().out


def test_missing_master_and_include_target(tmp_path: Path) -> None:
    write_tree(tmp_path)
    (tmp_path / "release-notes.adoc").unlink()
    (tmp_path / "backlog-web.adoc").write_text("include::docs/backlog/99-gone.adoc[]\n", "utf-8")

    errors = validate(tmp_path)

    assert "release-notes.adoc: master file is missing" in errors
    assert "backlog-web.adoc: include target not found: docs/backlog/99-gone.adoc" in errors
    assert "docs/backlog/01-chapter.adoc: not included by backlog-web.adoc" in errors


def test_unresolved_reference_and_duplicate_anchor(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    write_tree(
        tmp_path,
        requirement=REQUIREMENT + "\n[#FR-1.1]\n=== Again\n",
        tech="[#TS-1.1]\n=== Design\n\nImplements <<FR-9.9>>.\n",
    )

    errors = validate(tmp_path)

    assert any("duplicate anchor FR-1.1" in error for error in errors)
    assert any("unresolved reference <<FR-9.9>>" in error for error in errors)
    assert main(["validate_specs.py", str(tmp_path)]) == 1
    assert "problem(s) found" in capsys.readouterr().err


def test_traceability_is_enforced(tmp_path: Path) -> None:
    write_tree(
        tmp_path,
        tech="[#TS-1.1]\n=== Design\n\nNo requirement.\n",
        story="[#US-1.1]\n=== Story\n\nOnly <<FR-1.1>>.\n",
    )

    errors = validate(tmp_path)

    assert "docs/tech-specifications/01-chapter.adoc: TS-1.1 references no requirement" in errors
    assert "docs/backlog/01-chapter.adoc: US-1.1 references no technical specification" in errors


def test_anchor_in_the_wrong_folder(tmp_path: Path) -> None:
    write_tree(
        tmp_path, requirement=REQUIREMENT + "\n[#US-7.1]\n=== Misplaced <<TS-1.1>> <<FR-1.1>>\n"
    )

    assert any("US-7.1 does not belong in docs/specifications" in e for e in validate(tmp_path))
