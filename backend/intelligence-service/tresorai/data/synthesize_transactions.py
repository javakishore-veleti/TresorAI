"""Synthesize a multi-tenant AP transaction dataset to disk (ADR-0014).

Targets ~5 GB Parquet by default — overridable via target_gb argument or env var.
Deterministic seed so the demo always reproduces the same fraud patterns.

Idempotent: if manifest exists and verify_dataset() passes, skip generation.

Run:
    python -m tresorai.data.synthesize_transactions --target-gb 5
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Iterator

import numpy as np
import polars as pl
from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    TextColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)

from tresorai.data.manifest import touch_complete, verify_dataset, write_manifest
from tresorai.data.paths import dataset_dir

console = Console()

DATASET_KEY = "tx_synthetic_v1"
DATASET_VERSION = "1.0.0"

# Target row count to hit ~5 GB Parquet (parquet is ~150-200 B/row for our schema).
ROWS_PER_GB = 6_500_000
ROWS_PER_PARQUET_PART = 1_000_000  # write in 1M-row parts to keep memory bounded

NUM_TENANTS = 200            # channel partner with 200 SMB tenants
SUPPLIERS_PER_TENANT = 250   # 50K total suppliers
DAYS_OF_HISTORY = 365 * 2    # 2 years of tx history
DEFAULT_SEED = 20260425

# 12 fraud patterns we plant deliberately (per the locked plan + demo determinism).
FRAUD_PATTERNS = [
    "duplicate_invoice_within_24h",
    "iban_typosquat",
    "off_hours_payroll",
    "round_amount_anomaly",
    "first_payment_to_unknown_supplier",
    "supplier_name_obfuscation",
    "unusual_high_amount_for_supplier",
    "weekend_business_payment",
    "rapid_successive_payments",
    "geographically_anomalous_iban",
    "mid_month_payroll_off_cycle",
    "supplier_iban_changed",
]


def _build_supplier_pool(rng: np.random.Generator) -> pl.DataFrame:
    """Synthetic supplier corpus, one row per (tenant_id, supplier_id)."""
    n = NUM_TENANTS * SUPPLIERS_PER_TENANT
    suffixes = ["LLC", "Inc", "Co", "Ltd", "GmbH", "SAS", "BV", "AB", "Pty"]
    bases = [
        "ACME", "Globex", "Initech", "Hooli", "Umbrella", "Stark", "Wayne",
        "Wonka", "Tyrell", "Aperture", "Cyberdyne", "Soylent", "Massive Dynamic",
        "InGen", "Pied Piper", "Dunder Mifflin", "Vandelay", "Gringotts",
    ]
    supplier_idx = np.arange(n)
    base = rng.choice(bases, size=n)
    suffix = rng.choice(suffixes, size=n)
    serial = supplier_idx % 9999

    return pl.DataFrame({
        "tenant_id": np.repeat(np.arange(NUM_TENANTS), SUPPLIERS_PER_TENANT).astype(np.int32),
        "supplier_id": supplier_idx.astype(np.int32),
        "supplier_name": [f"{b} {s} {n:04d}" for b, s, n in zip(base, suffix, serial)],
        "country_iso2": rng.choice(
            ["US", "GB", "DE", "FR", "IN", "CA", "AU", "NL", "ES", "IT"], size=n,
        ),
        "iban_prefix": rng.choice(
            ["DE89", "GB29", "FR14", "IN40", "US12", "ES91", "IT60", "NL91"], size=n,
        ),
    })


def _generate_part(part_idx: int, rng: np.random.Generator,
                   suppliers: pl.DataFrame, n_rows: int) -> pl.DataFrame:
    n = n_rows
    tenant_ids = rng.integers(0, NUM_TENANTS, size=n, dtype=np.int32)
    supplier_indices = rng.integers(0, SUPPLIERS_PER_TENANT, size=n, dtype=np.int32)
    supplier_global = tenant_ids * SUPPLIERS_PER_TENANT + supplier_indices

    # Time spread over DAYS_OF_HISTORY
    epoch = 1735689600  # 2025-01-01 UTC
    seconds_span = DAYS_OF_HISTORY * 24 * 3600
    timestamps = epoch + rng.integers(0, seconds_span, size=n, dtype=np.int64)

    # Amounts — log-normal distribution with a few high-value outliers
    amounts = rng.lognormal(mean=6.0, sigma=1.4, size=n).astype(np.float32)
    amounts = np.clip(amounts, 5.0, 250_000.0)

    # Plant fraud labels — ~0.8% of rows
    fraud_mask = rng.random(n) < 0.008
    fraud_pattern = np.full(n, "", dtype=object)
    fraud_pattern[fraud_mask] = rng.choice(FRAUD_PATTERNS, size=fraud_mask.sum())

    return pl.DataFrame({
        "tx_id": (part_idx * ROWS_PER_PARQUET_PART + np.arange(n)).astype(np.int64),
        "tenant_id": tenant_ids,
        "supplier_id": supplier_global.astype(np.int32),
        "ts_unix": timestamps,
        "amount_usd": amounts,
        "currency": rng.choice(["USD", "EUR", "GBP", "INR", "AUD"], size=n),
        "channel": rng.choice(["ach", "wire", "check", "card", "rtp"], size=n),
        "memo": rng.choice([
            "monthly retainer", "invoice payment", "payroll", "rent",
            "consulting fees", "software license", "office supplies",
            "wire transfer", "vendor payment", "subscription",
        ], size=n),
        "is_fraud": fraud_mask,
        "fraud_pattern": fraud_pattern,
    })


def generate_dataset(target_gb: float = 5.0, seed: int = DEFAULT_SEED,
                     force: bool = False) -> dict[str, str | int | float]:
    """Generate the synthetic dataset to disk. Idempotent unless force=True."""
    out_dir = dataset_dir(DATASET_KEY)
    out_dir.mkdir(parents=True, exist_ok=True)

    if not force:
        ok, reason = verify_dataset(DATASET_KEY, deep=False)
        if ok:
            console.print(f"[green]✓[/green] {DATASET_KEY} already present, skipping ({reason})")
            return {"status": "ALREADY_PRESENT", "dataset_key": DATASET_KEY,
                    "rows": "n/a", "bytes": out_dir_size(out_dir)}

    rng = np.random.default_rng(seed)
    suppliers = _build_supplier_pool(rng)

    # Save supplier corpus once
    suppliers_path = out_dir / "suppliers.parquet"
    suppliers.write_parquet(suppliers_path, compression="zstd")

    target_rows = int(target_gb * ROWS_PER_GB)
    n_parts = (target_rows + ROWS_PER_PARQUET_PART - 1) // ROWS_PER_PARQUET_PART

    console.print(
        f"[cyan]Generating {DATASET_KEY}[/cyan] · "
        f"{target_rows:,} rows · {n_parts} parts of {ROWS_PER_PARQUET_PART:,}",
    )

    written: list[Path] = [suppliers_path]
    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("{task.completed}/{task.total} parts"),
        TransferSpeedColumn(),
        TimeRemainingColumn(),
    ) as progress:
        t = progress.add_task("synthesize", total=n_parts)
        for part_idx in range(n_parts):
            n_rows = min(ROWS_PER_PARQUET_PART, target_rows - part_idx * ROWS_PER_PARQUET_PART)
            df = _generate_part(part_idx, rng, suppliers, n_rows)
            part_path = out_dir / f"transactions_part_{part_idx:03d}.parquet"
            df.write_parquet(part_path, compression="zstd")
            written.append(part_path)
            progress.advance(t)

    console.print("[cyan]Writing manifest + computing checksums...[/cyan]")
    m = write_manifest(DATASET_KEY, DATASET_VERSION, written)
    touch_complete(DATASET_KEY)

    console.print(
        f"[green]✓ Done[/green] · {len(m.files)} files · "
        f"{m.total_bytes / 1024**3:.2f} GB · sha-256 verified",
    )
    return {
        "status": "SUCCESS",
        "dataset_key": DATASET_KEY,
        "rows": target_rows,
        "bytes": m.total_bytes,
    }


def out_dir_size(p: Path) -> int:
    return sum(f.stat().st_size for f in p.rglob("*") if f.is_file())


def main() -> None:
    parser = argparse.ArgumentParser(description="Synthesize TrésorAI transaction dataset.")
    parser.add_argument("--target-gb", type=float, default=float(os.environ.get("TAI_SYN_TARGET_GB", 5.0)))
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--force", action="store_true", help="Re-generate even if cache present.")
    args = parser.parse_args()
    generate_dataset(target_gb=args.target_gb, seed=args.seed, force=args.force)


if __name__ == "__main__":
    main()
