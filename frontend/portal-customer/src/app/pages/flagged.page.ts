import { Component, inject } from '@angular/core';
import { DecimalPipe } from '@angular/common';
import { TaiAlertComponent, TaiStatusPillComponent, TaiToastService } from '../primitives';

interface Flag {
  id: string;
  merchant: string;
  amount: number;
  signal: string;
  flaggedAt: string;
}

@Component({
  selector: 'tai-flagged-page',
  standalone: true,
  imports: [DecimalPipe, TaiAlertComponent, TaiStatusPillComponent],
  template: `
    <header class="mb-6">
      <h1 class="text-3xl font-semibold text-forest tracking-tight">Flagged transactions</h1>
      <p class="mt-1 text-bronze">
        Review the agent's recommendations. Hold / Release / Alert — your call, audit-logged.
        <span class="font-mono text-xs text-mauve ml-2">[T22 — review modal lands here]</span>
      </p>
    </header>

    <tai-alert variant="warning" class="mb-6 block">
      <strong class="text-forest">3 transactions awaiting review.</strong>
      Decisions are persisted to the audit log even before backend wiring lands.
    </tai-alert>

    <div class="space-y-3">
      @for (f of flags; track f.id) {
        <div class="rounded-tai border border-sand bg-surface-elevated shadow-tai-card p-5 flex items-center gap-4">
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-3">
              <tai-status-pill status="flagged">flagged</tai-status-pill>
              <span class="font-semibold text-forest truncate">{{ f.merchant }}</span>
              <span class="font-mono text-bronze">$ {{ f.amount | number:'1.2-2' }}</span>
            </div>
            <div class="mt-1 text-sm text-bronze">{{ f.signal }} · flagged {{ f.flaggedAt }}</div>
          </div>
          <div class="flex items-center gap-2 shrink-0">
            <button class="px-3 py-2 rounded-tai-sm text-sm font-medium border border-mauve text-forest hover:bg-surface-cream"
              (click)="act(f, 'hold')">Hold</button>
            <button class="px-3 py-2 rounded-tai-sm text-sm font-medium border border-mint text-forest hover:bg-surface-cream"
              (click)="act(f, 'release')">Release</button>
            <button class="px-3 py-2 rounded-tai-sm text-sm font-medium border border-coral text-forest hover:bg-coral-bg"
              (click)="act(f, 'alert')">Alert</button>
          </div>
        </div>
      }
    </div>
  `,
})
export class FlaggedPageComponent {
  private toast = inject(TaiToastService);

  flags: Flag[] = [
    { id: '1', merchant: 'A.C.M.E Office Suplys', amount: 412.55,   signal: 'IBAN typosquat · duplicate amount', flaggedAt: '2 min ago' },
    { id: '2', merchant: 'Cloud Hosting Co',      amount: 2400.00,  signal: 'first payment to supplier',         flaggedAt: '5 min ago' },
    { id: '3', merchant: 'Payroll · April batch 2', amount: 18234.10, signal: 'off-hours payroll run',          flaggedAt: '8 min ago' },
  ];

  act(f: Flag, action: 'hold' | 'release' | 'alert') {
    const variant = action === 'release' ? 'success' : action === 'alert' ? 'error' : 'warning';
    this.toast.show(`Decision recorded: ${action.toUpperCase()} · ${f.merchant}`, variant);
  }
}
