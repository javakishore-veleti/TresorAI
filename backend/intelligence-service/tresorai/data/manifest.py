"""Manifest reader/writer + checksum verification (ADR-0014).

The manifest is the source of truth for "is this dataset present and intact?".
Format:
{
  "dataset_key": "tx_synthetic_v1",
  "version": "1.0.0",
  "total_bytes": 5497558138,
  "files": [
    { "name": "transactions_part_01.parquet", "size_bytes": ..., "sha256": "..." },
    ...
  ]
}
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable

from tresorai.data.paths import complete_marker, dataset_dir, manifest_path


@dataclass
class FileEntry:
    name: str
    size_bytes: int
    sha256: str


@dataclass
class Manifest:
    dataset_key: str
    version: str
    total_bytes: int
    files: list[FileEntry]


def sha256_of(path: Path, chunk_size: int = 8 * 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(chunk_size):
            h.update(chunk)
    return h.hexdigest()


def write_manifest(dataset_key: str, version: str, files: Iterable[Path]) -> Manifest:
    """Build a manifest from real files on disk and write it next to them."""
    file_entries: list[FileEntry] = []
    for f in files:
        size = f.stat().st_size
        digest = sha256_of(f)
        file_entries.append(FileEntry(name=f.name, size_bytes=size, sha256=digest))

    total = sum(fe.size_bytes for fe in file_entries)
    m = Manifest(dataset_key=dataset_key, version=version, total_bytes=total, files=file_entries)

    manifest_path(dataset_key).write_text(
        json.dumps(asdict(m), indent=2) + "\n",
        encoding="utf-8",
    )
    return m


def read_manifest(dataset_key: str) -> Manifest | None:
    p = manifest_path(dataset_key)
    if not p.exists():
        return None
    raw = json.loads(p.read_text())
    return Manifest(
        dataset_key=raw["dataset_key"],
        version=raw["version"],
        total_bytes=raw["total_bytes"],
        files=[FileEntry(**f) for f in raw["files"]],
    )


def verify_dataset(dataset_key: str, *, deep: bool = True) -> tuple[bool, str]:
    """Return (ok, reason). `deep=True` recomputes sha-256 (slow but authoritative).

    With deep=False we only check file presence + size — fast 'is it probably ok?' for the
    Airflow short-circuit path. The DAG can run a deep verify weekly.
    """
    m = read_manifest(dataset_key)
    if m is None:
        return False, "no_manifest"

    d = dataset_dir(dataset_key)
    for fe in m.files:
        f = d / fe.name
        if not f.exists():
            return False, f"missing_file:{fe.name}"
        if f.stat().st_size != fe.size_bytes:
            return False, f"size_mismatch:{fe.name}"
        if deep and sha256_of(f) != fe.sha256:
            return False, f"sha256_mismatch:{fe.name}"

    if not complete_marker(dataset_key).exists():
        return False, "no_complete_marker"

    return True, "ok"


def touch_complete(dataset_key: str) -> None:
    complete_marker(dataset_key).touch()
