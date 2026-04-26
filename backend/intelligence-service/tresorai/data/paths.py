"""Path conventions for the local dataset cache (ADR-0014).

All cached datasets live OUTSIDE the repo at:
    $HOME/runtime_data/tresorai/datasets/<dataset_key>/

This survives `git clean -fdx` and full repo reinstalls.
Override with TAI_DATASETS_ROOT if needed (CI, alternate disk, etc.).
"""

from __future__ import annotations

import os
from pathlib import Path


def datasets_root() -> Path:
    override = os.environ.get("TAI_DATASETS_ROOT")
    if override:
        return Path(override).expanduser().resolve()
    return Path.home() / "runtime_data" / "tresorai" / "datasets"


def dataset_dir(dataset_key: str) -> Path:
    return datasets_root() / dataset_key


def manifest_path(dataset_key: str) -> Path:
    return dataset_dir(dataset_key) / "manifest.json"


def complete_marker(dataset_key: str) -> Path:
    return dataset_dir(dataset_key) / "_COMPLETE"
