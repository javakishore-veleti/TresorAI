import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import {
  TaiAccordionComponent,
  TaiAlertComponent,
  TaiStatusPillComponent,
  TaiToastService,
} from '../primitives';

interface Dataset {
  key: string;
  title: string;
  subtitle: string;
  source: string;
  target: string;
  rows: number | null;
  lastRunAt: string | null;
  status: 'never' | 'success' | 'pending' | 'flagged';
  initialOpen: boolean;
}

@Component({
  selector: 'tai-initial-downloads-page',
  standalone: true,
  imports: [FormsModule, TaiAccordionComponent, TaiAlertComponent, TaiStatusPillComponent],
  host: { class: 'block w-full max-w-5xl' },
  template: `
    <header class="mb-6">
      <div class="text-xs uppercase tracking-wide text-bronze font-semibold">
        Administration / Data Management
      </div>
      <h1 class="mt-1 text-3xl font-semibold text-forest tracking-tight">Initial Downloads</h1>
      <p class="mt-1 text-bronze max-w-3xl">
        Parameterized, idempotent, audited install of every reference dataset TrésorAI depends on.
        Run these once per client install. Re-running is a no-op when the source hash matches.
      </p>
    </header>

    <tai-alert variant="info" class="mb-6 block">
      <strong class="text-forest">No ad-hoc downloads</strong> — every reference data load runs from this page
      or its CLI counterpart. See <a class="text-brand-emerald-700 underline underline-offset-2"
        href="https://github.com/javakishore-veleti/TresorAI/blob/main/docs/adr/0007-no-adhoc-downloads-install-discipline.md"
        target="_blank" rel="noopener">ADR-0007</a>.
    </tai-alert>

    <div class="space-y-4">
      @for (d of datasets; track d.key) {
        <tai-accordion [title]="d.title" [subtitle]="d.subtitle" [initialOpen]="d.initialOpen">
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div class="space-y-4">
              <label class="block">
                <span class="block text-xs uppercase tracking-wide text-bronze font-semibold mb-1.5">Source URL</span>
                <input
                  type="text"
                  [(ngModel)]="d.source"
                  class="w-full rounded-tai-sm border border-sand bg-surface-pearl px-3 py-2 text-sm text-forest focus:border-brand-emerald-500 focus:ring-0"
                />
              </label>
              <label class="block">
                <span class="block text-xs uppercase tracking-wide text-bronze font-semibold mb-1.5">Target table</span>
                <input
                  type="text"
                  [(ngModel)]="d.target"
                  class="w-full rounded-tai-sm border border-sand bg-surface-pearl px-3 py-2 text-sm font-mono text-forest focus:border-brand-emerald-500 focus:ring-0"
                />
              </label>
            </div>
            <div class="space-y-3">
              <div class="rounded-tai-sm bg-surface-cream border border-sand p-4">
                <div class="text-xs uppercase tracking-wide text-bronze font-semibold mb-2">Last run</div>
                @if (d.lastRunAt) {
                  <div class="flex items-center gap-3">
                    <tai-status-pill [status]="d.status === 'success' ? 'released' : d.status === 'pending' ? 'pending' : 'flagged'">
                      {{ d.status }}
                    </tai-status-pill>
                    <div>
                      <div class="text-sm text-forest">{{ d.lastRunAt }}</div>
                      <div class="text-xs text-bronze font-mono">{{ d.rows }} rows · sha-256 verified</div>
                    </div>
                  </div>
                } @else {
                  <div class="text-sm text-bronze italic">Never run on this install.</div>
                }
              </div>
              <div class="flex items-center gap-2">
                <button
                  type="button"
                  class="px-4 py-2 rounded-tai-sm text-sm font-medium border border-mauve text-forest hover:bg-surface-cream"
                  (click)="dryRun(d)"
                >Dry run</button>
                <button
                  type="button"
                  class="px-4 py-2 rounded-tai-sm text-sm font-medium bg-brand-emerald-700 text-surface-pearl hover:bg-brand-emerald-500"
                  (click)="run(d)"
                >Run download</button>
              </div>
            </div>
          </div>
        </tai-accordion>
      }
    </div>

    <footer class="mt-8 text-xs text-bronze font-mono">
      Backend wires up at T22b (admin/initial-downloads UI) + T22c (api-gateway endpoints, audited).
    </footer>
  `,
})
export class InitialDownloadsPageComponent {
  private toast = inject(TaiToastService);

  datasets: Dataset[] = [
    {
      key: 'suppliers',
      title: 'Supplier reference list',
      subtitle: 'Seed pgvector with the legit supplier corpus for embedding similarity matching',
      source: 'gs://tresorai-reference/suppliers/v3.csv',
      target: 'public.suppliers',
      rows: 1840,
      lastRunAt: '2026-04-23 09:14 UTC',
      status: 'success',
      initialOpen: true,
    },
    {
      key: 'iban-typosquat',
      title: 'IBAN typosquat lookup',
      subtitle: 'Known-bad IBAN patterns and look-alike supplier domains',
      source: 'gs://tresorai-reference/iban-typosquat/v7.json',
      target: 'public.iban_typosquat',
      rows: null,
      lastRunAt: null,
      status: 'never',
      initialOpen: false,
    },
    {
      key: 'demo-seed',
      title: 'Demo seed data',
      subtitle: '5000 synthetic transactions across 200 suppliers + 12 planted fraud patterns',
      source: 'gs://tresorai-reference/demo-seed/v1.tar.gz',
      target: 'public.transactions, public.suppliers',
      rows: 5000,
      lastRunAt: '2026-04-21 13:42 UTC',
      status: 'success',
      initialOpen: false,
    },
  ];

  dryRun(d: Dataset) {
    this.toast.show(`Dry-run scheduled for ${d.title}`, 'info');
  }

  run(d: Dataset) {
    this.toast.show(`Running ${d.title} → ${d.target}`, 'success');
  }
}
