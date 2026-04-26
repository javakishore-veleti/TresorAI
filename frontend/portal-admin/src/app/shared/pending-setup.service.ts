import { Injectable, computed, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { catchError, of, tap } from 'rxjs';

export interface PendingDataset {
  key: string;
  title: string;
  required: boolean;
  approxSizeGb: number;
  currentStatus?: string;
}

interface AdminApiDatasetEntry {
  key: string;
  title: string;
  subtitle: string | null;
  required: boolean;
  approx_size_bytes: number;
  airflow_dag_id: string;
  target_table: string | null;
  current_status: string;
  rows_loaded: number | null;
  first_loaded_at: string | null;
  last_run_at: string | null;
}

const STUB_FALLBACK: PendingDataset[] = [
  { key: 'tx_synthetic_v1',     title: 'Synthetic transactions (~5 GB)',         required: true,  approxSizeGb: 5 },
  { key: 'ofac_sanctions',      title: 'OFAC + EU consolidated sanctions',       required: true,  approxSizeGb: 0.02 },
  { key: 'iban_typosquat',      title: 'IBAN typosquat lookup',                  required: true,  approxSizeGb: 0.001 },
  { key: 'paysim_extended',     title: 'PaySim extended fraud dataset (~5 GB)',  required: true,  approxSizeGb: 5 },
  { key: 'yelp_supplier',       title: 'Yelp supplier corpus (~10 GB)',          required: false, approxSizeGb: 10 },
  { key: 'iso_country_codes',   title: 'ISO 3166 country codes',                 required: true,  approxSizeGb: 0.0001 },
  { key: 'eval_set_curated',    title: 'Agent quality eval set',                 required: true,  approxSizeGb: 0.0002 },
];

const LOADED_STATUSES = new Set(['already_present', 'success']);
const ADMIN_API = 'http://localhost:8091';

@Injectable({ providedIn: 'root' })
export class PendingSetupService {
  private http = inject(HttpClient);

  pending = signal<PendingDataset[]>(STUB_FALLBACK);
  loaded = signal(false);

  hasPending = computed(() => this.pending().length > 0);
  requiredPendingCount = computed(() => this.pending().filter(d => d.required).length);
  totalPendingGb = computed(() =>
    this.pending().reduce((acc, d) => acc + d.approxSizeGb, 0),
  );

  constructor() {
    this.refresh();
  }

  /** Fetch from admin-api; fall back to stub if the service isn't reachable yet. */
  refresh(): void {
    this.http
      .get<AdminApiDatasetEntry[]>(`${ADMIN_API}/api/admin/initial-downloads/datasets`)
      .pipe(
        tap(rows => {
          const stillPending = rows
            .filter(r => !LOADED_STATUSES.has(r.current_status))
            .map<PendingDataset>(r => ({
              key: r.key,
              title: r.title,
              required: r.required,
              approxSizeGb: r.approx_size_bytes / 1024 ** 3,
              currentStatus: r.current_status,
            }));
          this.pending.set(stillPending);
          this.loaded.set(true);
        }),
        catchError(() => {
          // admin-api not running yet — keep the stub fallback in place.
          this.loaded.set(true);
          return of(null);
        }),
      )
      .subscribe();
  }

  markLoaded(key: string): void {
    this.pending.update(arr => arr.filter(d => d.key !== key));
  }
}
