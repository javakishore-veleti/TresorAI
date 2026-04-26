"""Unified CLI for dataset operations — `python -m tresorai.data.cli <verb>`."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from rich.console import Console
from rich.table import Table

from tresorai.data.manifest import read_manifest, verify_dataset
from tresorai.data.paths import dataset_dir, datasets_root

console = Console()


def _human_bytes(n: int) -> str:
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} PB"


def cmd_status() -> int:
    root = datasets_root()
    table = Table(title=f"Dataset cache · {root}")
    table.add_column("Dataset")
    table.add_column("Version")
    table.add_column("Files")
    table.add_column("Size")
    table.add_column("Status")

    if not root.exists():
        console.print(f"[yellow]No cache yet at {root}[/yellow]")
        return 0

    for entry in sorted(root.iterdir()):
        if not entry.is_dir():
            continue
        m = read_manifest(entry.name)
        ok, reason = verify_dataset(entry.name, deep=False)
        if m is None:
            table.add_row(entry.name, "—", "—", "—", "[red]NO_MANIFEST[/red]")
        else:
            status = "[green]OK[/green]" if ok else f"[red]{reason}[/red]"
            table.add_row(
                entry.name,
                m.version,
                str(len(m.files)),
                _human_bytes(m.total_bytes),
                status,
            )

    console.print(table)
    return 0


def cmd_synthesize(target_gb: float, force: bool) -> int:
    from tresorai.data import synthesize_transactions
    synthesize_transactions.generate_dataset(target_gb=target_gb, force=force)
    return 0


def cmd_ofac(force: bool) -> int:
    from tresorai.data import download_ofac
    download_ofac.download(force=force)
    return 0


def cmd_all(target_gb: float, force: bool) -> int:
    rc = cmd_synthesize(target_gb, force)
    rc |= cmd_ofac(force)
    return rc


def main() -> int:
    parser = argparse.ArgumentParser(prog="tresorai.data")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("status", help="Show local dataset cache status")
    sp = sub.add_parser("synthesize", help="Generate synthetic tx dataset")
    sp.add_argument("--target-gb", type=float, default=5.0)
    sp.add_argument("--force", action="store_true")
    sp = sub.add_parser("ofac", help="Download OFAC + EU sanctions lists")
    sp.add_argument("--force", action="store_true")
    sp = sub.add_parser("all", help="Run synthesize + ofac")
    sp.add_argument("--target-gb", type=float, default=5.0)
    sp.add_argument("--force", action="store_true")

    args = parser.parse_args()
    match args.cmd:
        case "status":     return cmd_status()
        case "synthesize": return cmd_synthesize(args.target_gb, args.force)
        case "ofac":       return cmd_ofac(args.force)
        case "all":        return cmd_all(args.target_gb, args.force)
        case _: parser.print_help(); return 1


if __name__ == "__main__":
    sys.exit(main())
