#!/usr/bin/env python3
"""Check a source bundle against the limits the Eval Platform's build agent enforces.

The build agent unpacks an attached archive and parses every member. Its limits are
hard: one unsupported file type raises and takes the whole archive's parse down with
it, so a bundle that looks fine can deliver nothing. This checks the same rules before
the user uploads.

Mirrors services/agent/file_to_content.py in the eval_platform_api project:
MAX_ARCHIVE_FILES, MAX_ARCHIVE_DEPTH, TEXT_CONTENT_MAX_LENGTH and file_to_sections'
dispatch table.

Usage:  python check_bundle.py <path-to-zip>
Exit 0 = shippable (warnings may still be printed), 1 = will fail or degrade.
"""

from __future__ import annotations

import sys
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

# The platform's live limits. Changing these here only hides a real failure.
MAX_ARCHIVE_FILES = 30
MAX_ARCHIVE_DEPTH = 1
TEXT_CONTENT_MAX_LENGTH = 50_000

ARCHIVE_SUFFIXES = {".zip", ".tar.gz", ".tgz", ".gz"}

# Suffixes with a dedicated parser. Anything outside this set survives only if it
# sniffs as plain text, which is why .csv and .json are not listed but do work.
PARSED_SUFFIXES = {
    ".pdf",
    ".docx",
    ".pptx",
    ".pages",
    ".odt",
    ".rtf",
    ".odp",
    ".svg",
    ".xlsx",
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".psd",
    ".bmp",
    ".tiff",
    ".mp4",
    ".avi",
    ".mov",
    ".mkv",
    ".wmv",
    ".flv",
    ".mpeg",
    ".webm",
    ".gif",
    ".mp3",
    ".wav",
    ".aac",
    ".flac",
    ".m4a",
    ".mpga",
    ".ogg",
    ".pcm",
    ".html",
    ".htm",
    ".ipynb",
    ".npy",
    ".npz",
    ".txt",
    ".md",
    ".py",
    ".log",
    ".eml",
} | ARCHIVE_SUFFIXES

# Read as one flat run of text rather than with structure. Fine, but they spend the
# 50k budget quickly, and a spreadsheet loses its sheets and cells this way.
FLAT_TEXT_SUFFIXES = {".csv", ".tsv", ".json", ".yaml", ".yml", ".xml", ".ndjson", ".jsonl"}

REQUIRED_ROOT_DOCS = ("00_BRIEF.md", "01_SOURCES.md", "02_TASK_SEEDS.md")


@dataclass
class Report:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)


def is_hidden(name: str) -> bool:
    """The agent skips dotfiles and anything under a dot-directory."""
    return any(part.startswith(".") for part in Path(name).parts)


def looks_like_text(data: bytes) -> bool:
    """Approximates the agent's plain-text sniff: decodable and free of NUL bytes."""
    if b"\x00" in data:
        return False
    try:
        data.decode("utf-8")
    except UnicodeDecodeError:
        return False
    return True


def check(zip_path: Path) -> Report:
    report = Report()

    if not zip_path.exists():
        report.error(f"No such file: {zip_path}")
        return report
    if not zipfile.is_zipfile(zip_path):
        report.error(f"Not a ZIP archive: {zip_path}")
        return report

    with zipfile.ZipFile(zip_path) as archive:
        members = [i for i in archive.infolist() if not i.is_dir() and not is_hidden(i.filename)]

        if not members:
            report.error("Archive is empty once dotfiles are skipped.")
            return report

        if len(members) > MAX_ARCHIVE_FILES:
            report.error(
                f"{len(members)} files, but the agent rejects any archive over "
                f"{MAX_ARCHIVE_FILES}. Merge or drop {len(members) - MAX_ARCHIVE_FILES} of them."
            )

        root_names = {Path(i.filename).name for i in members if Path(i.filename).parent == Path(".")}
        for required in REQUIRED_ROOT_DOCS:
            if required not in root_names:
                report.error(f"Missing {required} at the archive root.")

        comment = archive.comment.decode("utf-8", errors="replace")
        if not any(f"eval_type={style}" in comment for style in ("qa", "document_input", "agentic")):
            report.warn(
                "No eval_type in the archive comment. Stamp it at packaging "
                '(archive.comment = b"optima eval_type=<qa|document_input|agentic>") '
                "so the upload screen starts the build agent without asking."
            )

        for info in members:
            name = info.filename
            suffix = Path(name).suffix.lower()

            if suffix in ARCHIVE_SUFFIXES:
                # Depth 1 means the outer archive is the one allowance; a nested
                # archive is opened, but anything nested inside THAT raises.
                report.warn(
                    f"{name}: an archive inside the archive. It is read, but nothing "
                    f"nested inside it is (depth limit {MAX_ARCHIVE_DEPTH}). Flatten it."
                )
                continue

            if suffix not in PARSED_SUFFIXES:
                data = archive.read(info)
                if looks_like_text(data):
                    if suffix not in FLAT_TEXT_SUFFIXES:
                        report.warn(
                            f"{name}: no dedicated parser, but it reads as plain text so it "
                            f"will come through unstructured."
                        )
                elif suffix == "":
                    report.error(
                        f"{name}: no extension and not plain text: unsupported, and one "
                        f"unsupported file fails the ENTIRE archive."
                    )
                else:
                    report.error(
                        f"{name}: '{suffix}' is not a supported type and is not plain text. "
                        f"One unsupported file fails the ENTIRE archive. Convert or remove it."
                    )
                    continue

            if suffix == ".csv":
                report.warn(
                    f"{name}: CSV arrives as one flat run of text. Convert to .xlsx to keep "
                    f"sheets and cells intact."
                )

            if suffix in FLAT_TEXT_SUFFIXES or suffix in {".txt", ".md", ".log", ".py", ".eml"}:
                size = info.file_size
                if size > TEXT_CONTENT_MAX_LENGTH:
                    report.warn(
                        f"{name}: {size:,} bytes, over the {TEXT_CONTENT_MAX_LENGTH:,}-character "
                        f"read limit. The tail is silently dropped. Split it or trim it."
                    )

            if suffix in {".html", ".htm"} and info.file_size > TEXT_CONTENT_MAX_LENGTH:
                report.warn(
                    f"{name}: {info.file_size:,} bytes of markup. The "
                    f"{TEXT_CONTENT_MAX_LENGTH:,}-character limit applies to extracted text, "
                    f"which is usually shorter than the markup. Verify or split, and flag it "
                    f"in the manifest if left in deliberately."
                )

        basenames: dict[str, list[str]] = {}
        for info in members:
            basenames.setdefault(Path(info.filename).name, []).append(info.filename)
        for base, paths in basenames.items():
            if len(paths) > 1:
                report.warn(f"{base}: same filename in {len(paths)} places ({', '.join(paths)}).")

        for info in members:
            stem = Path(info.filename).stem.lower()
            if stem in {"doc", "file", "untitled", "document", "export", "data"} or stem.rstrip("0123456789_-") in {
                "doc",
                "file",
                "img",
                "image",
                "sheet",
            }:
                report.warn(
                    f"{info.filename}: the name says nothing about the contents. The agent "
                    f"reads these names. Rename it to describe what it is."
                )

    return report


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2

    report = check(Path(sys.argv[1]).expanduser())

    for warning in report.warnings:
        print(f"WARN   {warning}")
    for error in report.errors:
        print(f"ERROR  {error}")

    if report.errors:
        print(f"\n{len(report.errors)} error(s). This bundle will fail or lose files on upload.")
        return 1

    print(f"\nOK. Bundle is shippable ({len(report.warnings)} warning(s)).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
