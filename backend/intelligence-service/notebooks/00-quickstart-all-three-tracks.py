"""TrésorAI · All-three-tracks quickstart.

Run as a notebook (VS Code / PyCharm / Jupyter — every # %% is a cell)
or as a plain script:
    python notebooks/00-quickstart-all-three-tracks.py

Touches:
  Track 1 — Classical ML  : XGBoost fraud classifier on synthetic tx
  Track 2 — Deep Learning : sentence-transformers embeddings + cosine similarity
  Track 3 — Generative AI : Gemini 2.0 Flash agent call (requires GEMINI_API_KEY)

Prereqs:
  1. conda env active   (source ./scripts/conda-activate.sh)
  2. deps installed     (npm run setup:python:deps)
  3. dataset present    (npm run datasets:synthesize  →  ~5 GB to ~/runtime_data/tresorai/datasets/tx_synthetic_v1/)
"""

# %% [Cell 0] env check — confirm everything we need is importable
import os
import sys
from pathlib import Path

print(f"Python: {sys.version}")
print(f"Working dir: {os.getcwd()}")

import numpy as np
import pandas as pd
import polars as pl
import sklearn, xgboost, lightgbm, joblib, shap                              # classical
import torch, transformers                                                    # deep learning
from sentence_transformers import SentenceTransformer                         # deep learning
import google.generativeai as genai                                           # generative ai
print("✓ All Track-1/2/3 deps loaded.")

# %% [Cell 1] Locate and peek the synthetic dataset
from tresorai.data.paths import dataset_dir, datasets_root
from tresorai.data.manifest import read_manifest, verify_dataset

DKEY = "tx_synthetic_v1"
manifest = read_manifest(DKEY)
ok, reason = verify_dataset(DKEY, deep=False)

print(f"Dataset root: {datasets_root()}")
print(f"Dataset dir:  {dataset_dir(DKEY)}")
print(f"Manifest:     {manifest.version if manifest else 'MISSING'}")
print(f"Verify:       {'OK' if ok else reason}")
if not ok:
    print("\nGenerate it with: python -m tresorai.data.cli synthesize --target-gb 5")
    raise SystemExit(0)

# %% [Cell 2] Load with polars (lazy, memory-friendly for 5+ GB)
ddir = dataset_dir(DKEY)
tx = pl.scan_parquet(str(ddir / "transactions_part_*.parquet"))
suppliers = pl.read_parquet(ddir / "suppliers.parquet")

n_rows = tx.select(pl.len()).collect().item()
print(f"Transactions rows: {n_rows:,}")
print(f"Suppliers rows:    {len(suppliers):,}")
print(tx.head(5).collect())

# %% [Cell 3] === TRACK 1 — Classical ML : XGBoost fraud classifier ===
import xgboost as xgb
from sklearn.metrics import roc_auc_score, classification_report
from sklearn.model_selection import train_test_split

# Sample a manageable slice for quick iteration; scale up later
sample = tx.select([
    "amount_usd", "tenant_id", "supplier_id", "ts_unix", "is_fraud",
]).filter(pl.col("is_fraud").is_not_null()).head(2_000_000).collect().to_pandas()

X = sample.drop(columns=["is_fraud"]).astype({"is_fraud_": "int64"} if "is_fraud_" in sample.columns else {})
y = sample["is_fraud"].astype(int)

X_train, X_test, y_train, y_test = train_test_split(
    sample.drop(columns=["is_fraud"]), y, test_size=0.2, random_state=42, stratify=y,
)

dtrain = xgb.DMatrix(X_train, label=y_train)
dtest = xgb.DMatrix(X_test, label=y_test)
booster = xgb.train(
    {"objective": "binary:logistic", "eval_metric": "auc",
     "max_depth": 6, "eta": 0.1, "scale_pos_weight": 100},
    dtrain, num_boost_round=50,
    evals=[(dtest, "test")], verbose_eval=10,
)
y_pred = booster.predict(dtest)
print(f"\nTrack 1 · XGBoost AUC: {roc_auc_score(y_test, y_pred):.4f}")

# %% [Cell 4] === TRACK 2 — Deep Learning : embedding similarity over suppliers ===
print("\nLoading sentence-transformers/all-MiniLM-L6-v2 (~22 MB) ...")
emb = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Compute embeddings for first 200 supplier names
names = suppliers["supplier_name"].head(200).to_list()
vectors = emb.encode(names, show_progress_bar=False, normalize_embeddings=True)
print(f"Embeddings: {vectors.shape}  (suppliers x dims)")

# Find nearest-neighbours for a given query — proves the embedding similarity path
query = names[0]
query_vec = emb.encode([query], normalize_embeddings=True)[0]
scores = vectors @ query_vec
top5 = np.argsort(scores)[::-1][:5]

print(f"\nTrack 2 · top-5 neighbours for '{query}':")
for i in top5:
    print(f"  {scores[i]:.4f}  ·  {names[i]}")

# %% [Cell 5] === TRACK 3 — Generative AI : Gemini 2.0 Flash agent call ===
api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
if not api_key:
    print("\n⚠  GEMINI_API_KEY not set — skipping Track 3.")
    print("   Get a key at https://aistudio.google.com/ and add it to .env or your shell.")
else:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash-exp")

    sample_tx = sample.iloc[0].to_dict()
    prompt = f"""You are a senior AP-fraud analyst at TrésorAI.
Score the following transaction for fraud risk on a 0-1 scale and return STRICT JSON only.

Transaction:
{sample_tx}

Schema:
{{
  "score": <float 0-1>,
  "decision": "<release|hold|alert>",
  "signals": [<short reason strings>],
  "confidence": <float 0-1>
}}
"""
    resp = model.generate_content(prompt)
    print(f"\nTrack 3 · Gemini response:\n{resp.text}")

# %% [Cell 6] Done — what's next
print("""
Next steps:
  • Tune XGBoost on the full 5 GB (cell 3 used a 2M-row slice).
  • Push embeddings into pgvector for proper similarity-with-payload queries.
  • Wrap Gemini in a tool-using agent (get_supplier_history / get_cash_position / get_similar_past_tx).
  • Each of these becomes its own DAG (see ADR-0012):
      Track 1: dag_xgboost_fraud_train
      Track 2: dag_embedding_finetune_train
      Track 3: dag_agent_eval_suite
""")
