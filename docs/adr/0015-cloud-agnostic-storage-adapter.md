# ADR-0015: Cloud-agnostic storage adapter for dataset fetches (GCS / S3 / Azure feature toggle)

- Status: Accepted
- Date: 2026-04-25

## Context
Different developers, different client engagements, and different channel partners run on different clouds. Hard-coding `gs://...` URLs in Airflow DAGs would force everyone onto GCP for local development and create rewrite work when a client mandates AWS or Azure as their data residency. We want one DAG codebase, one manifest schema, three storage backends.

The user directive *(2026-04-25)*: for local development, dataset fetches must support **GCS** *(Google Cloud Storage)*, **AWS S3**, and **Azure Blob Storage**, selectable via a feature toggle.

## Decision

### Storage abstraction interface

```python
class StorageAdapter(ABC):
    """Provider-neutral fetch interface used by all DAGs."""
    @abstractmethod
    def head(self, dataset_key: str, file_name: str) -> StorageObject: ...

    @abstractmethod
    def download(self, dataset_key: str, file_name: str, local_path: Path) -> None: ...

    @abstractmethod
    def list(self, dataset_key: str) -> list[StorageObject]: ...
```

Three implementations live under `backend/intelligence-service/tresorai/storage/`:

- `GcsStorageAdapter` — uses `google-cloud-storage` SDK; auth via Application Default Credentials or Workload Identity Federation
- `S3StorageAdapter` — uses `boto3`; auth via AWS SSO, IAM role, or `~/.aws/credentials`
- `AzureBlobStorageAdapter` — uses `azure-storage-blob`; auth via DefaultAzureCredential

### Feature-toggle selection

Driven by an env var `TAI_STORAGE_PROVIDER` with values `gcs` *(default)* / `s3` / `azure`:

```bash
# .env / docker-compose / cloud-run env
TAI_STORAGE_PROVIDER=gcs
TAI_STORAGE_BUCKET=tresorai-datasets
TAI_STORAGE_PREFIX=datasets/

# Provider-specific extras
TAI_GCS_PROJECT=tresorai-portfolio
TAI_AWS_REGION=us-east-1
TAI_AZURE_ACCOUNT=tresorai
TAI_AZURE_CONTAINER=datasets
```

A factory resolves the adapter at startup:

```python
def get_storage_adapter() -> StorageAdapter:
    provider = os.environ.get("TAI_STORAGE_PROVIDER", "gcs").lower()
    match provider:
        case "gcs":   return GcsStorageAdapter(...)
        case "s3":    return S3StorageAdapter(...)
        case "azure": return AzureBlobStorageAdapter(...)
        case _: raise ValueError(f"Unknown TAI_STORAGE_PROVIDER: {provider}")
```

Each provider's client is a project devDep, not a hard runtime dep — only the active provider's SDK is imported at runtime *(lazy import inside the adapter)*.

### Cloud-agnostic dataset manifest

The manifest in `data/datasets/<dataset_key>/manifest.source.json` is **provider-neutral**:

```json
{
  "dataset_key": "tx_synthetic_v1",
  "version": "1.0.0",
  "total_bytes": 5497558138,
  "files": [
    { "name": "transactions_part_01.parquet", "size_bytes": 1073741824, "sha256": "abc..." },
    { "name": "transactions_part_02.parquet", "size_bytes": 1073741824, "sha256": "def..." }
  ]
}
```

The adapter constructs the full URL at fetch time:

| Provider | URL form |
|---|---|
| GCS    | `gs://${BUCKET}/${PREFIX}${dataset_key}/${file.name}` |
| S3     | `s3://${BUCKET}/${PREFIX}${dataset_key}/${file.name}` |
| Azure  | `https://${ACCOUNT}.blob.core.windows.net/${CONTAINER}/${PREFIX}${dataset_key}/${file.name}` |

### Admin portal source-URL display

The Initial Downloads accordion's "Source URL" field becomes provider-aware: it shows the URL the active adapter will use, derived from the manifest plus the env config — not a hard-coded string.

## Consequences

- (+) **One DAG codebase** runs against any of three cloud providers locally; production stays on Vertex/GCS but the option is preserved.
- (+) **Client portability** — a channel partner on AWS can stand up TrésorAI without DAG rewrites; only IAM and bucket config change.
- (+) **Simpler local dev** — developers without a GCP project can point at an S3 bucket or even a local MinIO.
- (+) **Manifest stays clean** — no per-provider URLs leak into checked-in data files.
- (−) **Three SDKs to maintain.** Mitigated by lazy import — only the active provider's SDK is loaded at runtime.
- (−) **Auth surface area is bigger** — three credential models to document. Mitigated by a single section in `README_Developer_Notes.md` showing the env-var matrix per provider.
- (−) **Manifest doesn't carry the URL**, so a manifest cache hit on one machine does not re-validate that the source bucket on another machine still has the same file. Mitigated by sha-256 in the manifest — content matches regardless of provider.
