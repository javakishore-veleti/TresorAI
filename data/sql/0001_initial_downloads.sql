-- TrésorAI · admin-api migration 0001
--
-- Tables that back the Initial Downloads page in portal-admin and the
-- pending-setup banner. Status updates are written by Airflow callbacks
-- via the admin-api service. ADR-0014 + ADR-0012.

-- ---- Catalog: one row per dataset key
CREATE TABLE IF NOT EXISTS initial_downloads_datasets (
  key                text PRIMARY KEY,
  title              text NOT NULL,
  subtitle           text,
  required           boolean NOT NULL DEFAULT true,
  approx_size_bytes  bigint NOT NULL DEFAULT 0,

  airflow_dag_id     text NOT NULL,         -- which DAG handles this dataset
  source_uri         text,                  -- provider-neutral; resolved at fetch time
  target_table       text,                  -- where rows land after the load

  current_status     text NOT NULL DEFAULT 'never_loaded'
    CHECK (current_status IN
      ('never_loaded', 'missing_files', 'stale', 'running',
       'already_present', 'success', 'failed')),
  current_run_id     uuid,
  rows_loaded        bigint,
  source_hash_last   text,
  first_loaded_at    timestamptz,
  last_run_at        timestamptz,
  last_error         text,

  created_at         timestamptz NOT NULL DEFAULT now(),
  updated_at         timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_idd_status ON initial_downloads_datasets (current_status);

-- ---- History: one row per dataset run
CREATE TABLE IF NOT EXISTS initial_downloads_runs (
  id                 uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  dataset_key        text NOT NULL REFERENCES initial_downloads_datasets(key) ON DELETE CASCADE,
  airflow_dag_id     text NOT NULL,
  airflow_run_id     text,                  -- Airflow's dag_run_id

  status             text NOT NULL DEFAULT 'queued'
    CHECK (status IN
      ('queued', 'running', 'success', 'already_present', 'failed', 'cancelled')),

  forced             boolean NOT NULL DEFAULT false,    -- "Re-download (force)" path
  triggered_by       text,                              -- user email / system
  source_provider    text,                              -- gcs | s3 | azure (per ADR-0015)
  source_uri         text,
  target_table       text,

  rows_loaded        bigint,
  bytes_downloaded   bigint,
  source_hash        text,

  started_at         timestamptz NOT NULL DEFAULT now(),
  finished_at        timestamptz,
  duration_ms        integer,

  error_message      text,
  audit_log_url      text,

  created_at         timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_idr_dataset_started ON initial_downloads_runs (dataset_key, started_at DESC);
CREATE INDEX IF NOT EXISTS idx_idr_status ON initial_downloads_runs (status);

-- ---- Trigger: keep updated_at fresh on the catalog
CREATE OR REPLACE FUNCTION trg_initial_downloads_datasets_updated() RETURNS trigger AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_idd_updated_at ON initial_downloads_datasets;
CREATE TRIGGER trg_idd_updated_at
  BEFORE UPDATE ON initial_downloads_datasets
  FOR EACH ROW EXECUTE FUNCTION trg_initial_downloads_datasets_updated();

-- ---- Seed the catalog (idempotent — INSERT ... ON CONFLICT DO NOTHING)
INSERT INTO initial_downloads_datasets
  (key,                  title,                                       subtitle,                                                       required, approx_size_bytes,         airflow_dag_id,                target_table)
VALUES
  ('tx_synthetic_v1',    'Synthetic transactions (~5 GB)',           'Demo replay stream + classical-ML training corpus',            true,     5368709120,                'setup_demo_seed',          'public.transactions'),
  ('ofac_sanctions',     'OFAC + EU consolidated sanctions',          'Daily-refreshed sanctions lists for the rule layer',           true,       20971520,                'setup_ofac_eu_sanctions',        'public.sanctions'),
  ('iban_typosquat',     'IBAN typosquat lookup',                     'Curated IBAN lookalike patterns + supplier domains',           true,         524288,                'setup_iban_typosquat',     'public.iban_typosquat'),
  ('paysim_extended',    'PaySim extended fraud dataset (~5 GB)',    'Real-shape labelled fraud for XGBoost / Isolation Forest',     true,     5368709120,                'setup_paysim_extended',    'public.tx_paysim'),
  ('yelp_supplier',      'Yelp supplier corpus (~10 GB)',            'Embedding fine-tune corpus for Deep Learning track',           false,    10737418240,                'setup_yelp_supplier_corpus','public.suppliers_yelp'),
  ('iso_country_codes',  'ISO 3166 country codes',                    'Yearly-refresh reference data',                                 true,          10240,                'setup_iso_country_codes',  'public.country_codes'),
  ('eval_set_curated',   'Agent quality eval set',                    'Hand-curated (tx, expected_decision, citations) cases',        true,         204800,                'setup_agent_eval',        'public.agent_eval_cases')
ON CONFLICT (key) DO NOTHING;
