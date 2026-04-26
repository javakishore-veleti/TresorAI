import { Component, OnDestroy, OnInit, inject, signal } from '@angular/core';
import { DatePipe, DecimalPipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { interval, Subscription } from 'rxjs';

import {
  TaiAccordionComponent,
  TaiAlertComponent,
  TaiStatusPillComponent,
  TaiToastService,
} from '../primitives';
import { PendingSetupService } from '../shared/pending-setup.service';

interface DatasetEntry {
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
  last_run_id: string | null;
  last_run_progress: number | null;
}

interface RunRecord {
  id: string;
  dataset_key: string;
  airflow_dag_id: string;
  status: string;
  started_at: string;
  finished_at: string | null;
  duration_ms: number | null;
  forced: boolean;
  rows_loaded: number | null;
}

const ADMIN_API = 'http://localhost:8091';

const PILL_BY_STATUS: Record<string, 'released' | 'pending' | 'held' | 'flagged' | 'info'> = {
  never_loaded:    'flagged',
  missing_files:   'flagged',
  stale:           'pending',
  running:         'pending',
  queued:          'pending',
  already_present: 'released',
  success:         'released',
  failed:          'flagged',
};

@Component({
  selector: 'tai-initial-downloads-page',
  standalone: true,
  imports: [
    DatePipe, DecimalPipe, FormsModule,
    TaiAccordionComponent, TaiAlertComponent, TaiStatusPillComponent,
  ],
  host: { class: 'block w-full max-w-5xl' },
  template: `
    <header class="mb-6">
      <div class="text-xs uppercase tracking-wide text-bronze font-semibold">
        Administration / Data Management
      </div>
      <h1 class="mt-1 text-3xl font-semibold text-forest tracking-tight">Initial Downloads</h1>
      <p class="mt-1 text-bronze max-w-3xl">
        Parameterized, idempotent, audited install of every reference dataset TrésorAI depends on.
        Run these once per client install — re-running is a no-op when the source hash matches.
      </p>
    </header>

    @if (errorMsg()) {
      <tai-alert variant="error" class="mb-6 block">
        Could not reach admin-api at {{ adminApiUrl }}: {{ errorMsg() }}.
        <span class="text-bronze">The list below is the static catalog; Run download is disabled.</span>
      </tai-alert>
    } @else {
      <tai-alert variant="info" class="mb-6 block">
        <strong class="text-forest">No ad-hoc downloads</strong> — every dataset load runs from this page or its CLI counterpart.
        Status streams live from <code class="font-mono text-xs text-mauve">{{ adminApiUrl }}</code>.
      </tai-alert>
    }

    <div class="space-y-4">
      @for (d of datasets(); track d.key) {
        <tai-accordion
          [title]="d.title + (d.required ? '' : '  ·  optional')"
          [subtitle]="d.subtitle ?? ''"
          [initialOpen]="d.current_status === 'running' || d.current_status === 'never_loaded'"
        >
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <!-- Left: source / target -->
            <div class="space-y-3">
              <div>
                <span class="block text-xs uppercase tracking-wide text-bronze font-semibold mb-1">DAG ID</span>
                <code class="text-sm font-mono text-forest">{{ d.airflow_dag_id }}</code>
              </div>
              <div>
                <span class="block text-xs uppercase tracking-wide text-bronze font-semibold mb-1">Target table</span>
                <code class="text-sm font-mono text-forest">{{ d.target_table }}</code>
              </div>
              <div>
                <span class="block text-xs uppercase tracking-wide text-bronze font-semibold mb-1">Approx. size</span>
                <span class="text-sm text-forest">{{ formatBytes(d.approx_size_bytes) }}</span>
              </div>
            </div>

            <!-- Right: status + actions -->
            <div class="space-y-3">
              <div class="rounded-tai-sm bg-surface-cream border border-sand p-4">
                <div class="flex items-center gap-3 mb-2">
                  <span class="text-xs uppercase tracking-wide text-bronze font-semibold">Current status</span>
                  <tai-status-pill [status]="pillFor(d.current_status)">
                    {{ d.current_status }}
                  </tai-status-pill>
                </div>

                @if (d.current_status === 'running' && d.last_run_progress !== null) {
                  <div class="mt-2">
                    <div class="flex items-center justify-between mb-1 text-xs text-bronze">
                      <span>Downloading via Airflow</span>
                      <span class="font-mono">{{ d.last_run_progress }}%</span>
                    </div>
                    <div class="h-2 rounded-full bg-surface-pearl overflow-hidden border border-sand">
                      <div class="h-full bg-brand-emerald-500 transition-all duration-300"
                           [style.width.%]="d.last_run_progress ?? 0"></div>
                    </div>
                  </div>
                } @else if (d.last_run_at) {
                  <div class="text-sm text-forest">
                    Last run: <span class="font-mono">{{ d.last_run_at | date:'medium' }}</span>
                  </div>
                  @if (d.rows_loaded !== null) {
                    <div class="text-xs text-bronze font-mono">
                      {{ d.rows_loaded | number }} rows · sha-256 verified
                    </div>
                  }
                } @else {
                  <div class="text-sm text-bronze italic">Never run on this install.</div>
                }
              </div>

              <div class="flex items-center gap-2">
                <button
                  type="button"
                  class="px-4 py-2 rounded-tai-sm text-sm font-semibold bg-brand-emerald-700 text-surface-pearl hover:bg-brand-emerald-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  [disabled]="d.current_status === 'running' || !!errorMsg()"
                  (click)="run(d, false)"
                >
                  @if (d.current_status === 'running') {
                    Running…
                  } @else if (d.current_status === 'success' || d.current_status === 'already_present') {
                    Run again (cached)
                  } @else {
                    Run download
                  }
                </button>
                @if (d.current_status === 'success' || d.current_status === 'already_present') {
                  <button
                    type="button"
                    class="px-4 py-2 rounded-tai-sm text-sm font-medium border border-coral text-forest hover:bg-coral-bg transition-colors"
                    [disabled]="!!errorMsg()"
                    (click)="run(d, true)"
                  >
                    Re-download (force)
                  </button>
                }
              </div>
            </div>
          </div>
        </tai-accordion>
      }
    </div>

    <footer class="mt-8 text-xs text-bronze font-mono">
      Backend: admin-api on port 8091. Polling every {{ pollMs / 1000 }}s while any DAG is running.
    </footer>
  `,
})
export class InitialDownloadsPageComponent implements OnInit, OnDestroy {
  private http = inject(HttpClient);
  private toast = inject(TaiToastService);
  private pendingSvc = inject(PendingSetupService);

  adminApiUrl = ADMIN_API;
  pollMs = 1000;

  datasets = signal<DatasetEntry[]>([]);
  errorMsg = signal<string | null>(null);

  private pollSub?: Subscription;

  ngOnInit(): void {
    this.refresh();
    this.pollSub = interval(this.pollMs).subscribe(() => {
      const anyRunning = this.datasets().some(d => d.current_status === 'running');
      if (anyRunning || this.datasets().length === 0) {
        this.refresh();
      }
    });
  }

  ngOnDestroy(): void {
    this.pollSub?.unsubscribe();
  }

  refresh(): void {
    this.http.get<DatasetEntry[]>(`${ADMIN_API}/api/admin/initial-downloads/datasets`).subscribe({
      next: rows => {
        this.datasets.set(rows);
        this.errorMsg.set(null);
        this.pendingSvc.refresh();
      },
      error: err => {
        this.errorMsg.set(err?.statusText || err?.message || 'connection refused');
      },
    });
  }

  run(d: DatasetEntry, force: boolean): void {
    this.http
      .post<{ run_id: string; status: string }>(
        `${ADMIN_API}/api/admin/initial-downloads/${d.key}/run`,
        { force, triggered_by: 'admin@local' },
      )
      .subscribe({
        next: r => {
          const variant =
            r.status === 'already_present' ? 'success'
            : r.status === 'queued'        ? 'info'
            :                                'info';
          this.toast.show(
            r.status === 'already_present'
              ? `${d.title} — already present (audit-only run, <1 s)`
              : `${d.title} — queued via ${d.airflow_dag_id}`,
            variant,
          );
          this.refresh();
        },
        error: err => {
          this.toast.show(`Failed: ${err?.error?.detail ?? err?.message ?? 'error'}`, 'error');
        },
      });
  }

  pillFor(status: string): 'released' | 'pending' | 'held' | 'flagged' | 'info' {
    return PILL_BY_STATUS[status] ?? 'info';
  }

  formatBytes(n: number): string {
    if (n < 1024) return `${n} B`;
    if (n < 1024 ** 2) return `${(n / 1024).toFixed(1)} KB`;
    if (n < 1024 ** 3) return `${(n / 1024 ** 2).toFixed(1)} MB`;
    return `${(n / 1024 ** 3).toFixed(2)} GB`;
  }
}
