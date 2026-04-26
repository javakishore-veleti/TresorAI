# ADR-0014: Local dataset cache + idempotent Airflow loads

- Status: Accepted
- Date: 2026-04-25

## Context
TrésorAI's dataset footprint is **30–55 GB** of cached training/reference data per developer laptop *(see README §3 and [ADR-0012](./0012-airflow-for-initial-downloads.md))*. Re-downloading on every `git clean` or app reinstall is unacceptable — both for developer time and for source-bandwidth costs at scale.

The user requirement *(2026-04-25)*: clicking "Run download" in the admin portal on an already-loaded dataset must complete in **< 1 second** without touching the network. Airflow DAGs must short-circuit if local files already match the manifest.

## Decision

### File-system layout

All cached datasets live **outside the repo** at:

```
$HOME/runtime_data/tresorai/datasets/<dataset_key>/
                                   ├── manifest.json   (sha-256 per file, total bytes, version, fetched_from_provider)
                                   ├── <files...>      (parquet / csv / json / etc.)
                                   └── _COMPLETE       (touch-file marker; mtime = last successful sync)
```

Path matches the conda env convention (`$HOME/runtime_data/python_venvs/TresorAI` per [ADR-0009](./0009-conda-env-pinned-path.md)) — both survive `git clean -fdx` and full repo reinstalls.

### Airflow DAG idempotency pattern

Every dataset DAG starts with the same three tasks:

```
[check_local_files] ──► matches manifest? ──┐
                                            ├─ YES ──► [register_run: ALREADY_PRESENT] ──► [end]
                                            └─ NO  ──► [download_via_storage_adapter] ──►
                                                       [verify_checksums] ──►
                                                       [touch_complete] ──►
                                                       [register_run: SUCCESS]
```

`check_local_files` returns `skip_download=True` if **all** of these hold:
1. `<local>/manifest.json` exists and parses
2. Every file listed in the manifest exists on disk with the matching size
3. Every file's sha-256 matches the manifest *(checksum verification — cheap with mmap)*
4. `<local>/_COMPLETE` marker exists

A `BranchPythonOperator` then routes to `register_run_already_present` (audit-only) instead of the heavy `download_via_storage_adapter` (network + verify).

### Status model

The Postgres `initial_downloads_runs.status` enum captures the four lifecycle states the admin UI renders:

| Status | Meaning | UI pill |
|---|---|---|
| `never_loaded` | No manifest, no files | grey-equivalent *(actually mauve per ADR-0010)* |
| `missing_files` | Manifest present, files incomplete | amber |
| `stale` | Files present but manifest hash mismatches the source manifest version | amber |
| `running` | DAG in flight | sky |
| `already_present` | Check passed, no fetch, audit-only run *(success in <1 s)* | mint |
| `success` | Fresh download verified | mint |
| `failed` | DAG raised | coral |

### Force re-download

Admin UI exposes a separate **Re-download (force)** button that triggers the DAG with `dag_run_conf = { "force": true }`. The DAG skips `check_local_files` and re-fetches.

### Multi-developer behaviour

Each developer's laptop has its own cache. If one developer regenerates `tx_synthetic_v1` from a new seed, they bump the manifest `version` field; other developers' caches are then `stale` and the next "Run download" actually re-fetches.

## Consequences

- (+) **Re-clicking download is free.** Postgres still gets an audit row, but no bandwidth.
- (+) **Reinstalls don't re-download.** Cache lives outside the repo; `git clean -fdx` is non-destructive to data.
- (+) **Deterministic builds.** Manifest hash + version make "is my cache up-to-date?" a yes/no check, not a guess.
- (+) **Force-refresh is explicit.** Default flow is safe; destructive re-fetch requires a separate button + DAG conf flag.
- (−) **First-time install pulls 30–55 GB.** Slow on first onboarding. Mitigation: `npm run setup:initial:all` runs the loads in the background so the developer can start on UI work in parallel.
- (−) **Disk usage outside the repo.** Developers must monitor `~/runtime_data/`. Mitigation: a `npm run datasets:status` script that prints sizes per dataset and total.
