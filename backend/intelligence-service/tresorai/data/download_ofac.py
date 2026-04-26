"""Download OFAC SDN List + EU Consolidated Sanctions (real public data).

No auth required. ~10-20 MB combined. Idempotent (ADR-0014).

Run:
    python -m tresorai.data.download_ofac
"""

from __future__ import annotations

import argparse
from pathlib import Path

import httpx
from rich.console import Console
from tenacity import retry, stop_after_attempt, wait_exponential

from tresorai.data.manifest import touch_complete, verify_dataset, write_manifest
from tresorai.data.paths import dataset_dir

console = Console()

DATASET_KEY = "ofac_sanctions"
DATASET_VERSION = "1.0.0"

SOURCES = {
    # OFAC SDN — US Treasury
    "sdn_advanced.xml": "https://www.treasury.gov/ofac/downloads/sdn_advanced.xml",
    "cons_advanced.xml": "https://www.treasury.gov/ofac/downloads/cons_advanced.xml",
    # EU Consolidated Sanctions List (public XML)
    "eu_consolidated.xml": "https://webgate.ec.europa.eu/fsd/fsf/public/files/xmlFullSanctionsList_1_1/content?token=dG9rZW4tMjAxNw",
}


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=2, max=30))
def _fetch(url: str, dest: Path) -> int:
    with httpx.stream("GET", url, follow_redirects=True, timeout=120.0) as r:
        r.raise_for_status()
        n = 0
        with dest.open("wb") as f:
            for chunk in r.iter_bytes(chunk_size=1 << 16):
                f.write(chunk)
                n += len(chunk)
        return n


def download(force: bool = False) -> dict[str, str | int]:
    out_dir = dataset_dir(DATASET_KEY)
    out_dir.mkdir(parents=True, exist_ok=True)

    if not force:
        ok, reason = verify_dataset(DATASET_KEY, deep=False)
        if ok:
            console.print(f"[green]✓[/green] {DATASET_KEY} already present ({reason})")
            return {"status": "ALREADY_PRESENT", "dataset_key": DATASET_KEY}

    written: list[Path] = []
    for name, url in SOURCES.items():
        dest = out_dir / name
        console.print(f"[cyan]→[/cyan] {url}")
        try:
            size = _fetch(url, dest)
            console.print(f"  [green]✓[/green] {name} · {size/1024:.1f} KB")
            written.append(dest)
        except Exception as e:
            console.print(f"  [red]✗[/red] {name} · {e}")

    if not written:
        return {"status": "FAILED", "dataset_key": DATASET_KEY, "reason": "no_files_fetched"}

    write_manifest(DATASET_KEY, DATASET_VERSION, written)
    touch_complete(DATASET_KEY)
    console.print(f"[green]✓ Done[/green] · {DATASET_KEY}")
    return {"status": "SUCCESS", "dataset_key": DATASET_KEY, "files": len(written)}


def main() -> None:
    parser = argparse.ArgumentParser(description="Download OFAC + EU sanctions lists.")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    download(force=args.force)


if __name__ == "__main__":
    main()
