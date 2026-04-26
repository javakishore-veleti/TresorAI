import { Component, inject } from '@angular/core';
import { TaiAlertComponent, TaiStatusPillComponent, TaiToastService } from '../primitives';

interface DemoTx {
  id: string;
  merchant: string;
  amount: number;
  time: string;
  status: 'released' | 'pending' | 'held' | 'flagged';
  signal?: string;
}

@Component({
  selector: 'tai-stream-page',
  standalone: true,
  imports: [TaiAlertComponent, TaiStatusPillComponent],
  template: `
    <header class="mb-6">
      <h1 class="text-3xl font-semibold text-forest tracking-tight">Live transaction stream</h1>
      <p class="mt-1 text-bronze">
        Every outbound payment as it arrives, scored in under 200&nbsp;ms.
        <span class="font-mono text-xs text-mauve ml-2">[demo data — wires to /ws/stream at T13]</span>
      </p>
    </header>

    <tai-alert variant="info" class="mb-6 block">
      WebSocket stream not connected yet. Backend services scaffold at T04 (api-gateway) and T05 (ingest-service).
    </tai-alert>

    <div class="rounded-tai border border-sand bg-surface-elevated shadow-tai-card overflow-hidden">
      <table class="w-full text-sm">
        <thead class="bg-surface-cream text-bronze uppercase text-xs tracking-wide">
          <tr>
            <th class="text-left px-4 py-3 font-medium">Time</th>
            <th class="text-left px-4 py-3 font-medium">Merchant</th>
            <th class="text-right px-4 py-3 font-medium">Amount</th>
            <th class="text-left px-4 py-3 font-medium">Signal</th>
            <th class="text-left px-4 py-3 font-medium">Status</th>
            <th class="text-right px-4 py-3 font-medium">Actions</th>
          </tr>
        </thead>
        <tbody>
          @for (tx of demoTxs; track tx.id) {
            <tr class="border-t border-sand">
              <td class="px-4 py-3 font-mono text-xs text-bronze">{{ tx.time }}</td>
              <td class="px-4 py-3 text-forest">{{ tx.merchant }}</td>
              <td class="px-4 py-3 text-right font-mono text-forest">
                {{ tx.amount | number:'1.2-2' }} <span class="text-bronze">USD</span>
              </td>
              <td class="px-4 py-3 text-bronze text-xs">{{ tx.signal || '—' }}</td>
              <td class="px-4 py-3">
                <tai-status-pill [status]="tx.status">{{ tx.status }}</tai-status-pill>
              </td>
              <td class="px-4 py-3 text-right">
                <button
                  type="button"
                  class="text-xs font-medium text-brand-emerald-700 hover:text-brand-emerald-500"
                  (click)="onReview(tx)"
                >Review →</button>
              </td>
            </tr>
          }
        </tbody>
      </table>
    </div>
  `,
})
export class StreamPageComponent {
  private toast = inject(TaiToastService);

  demoTxs: DemoTx[] = [
    { id: '1', time: '14:02:11', merchant: 'ACME Office Supplies',     amount: 412.55,   status: 'released' },
    { id: '2', time: '14:02:43', merchant: 'TWILIO INC',               amount: 184.20,   status: 'released' },
    { id: '3', time: '14:03:09', merchant: 'A.C.M.E Office Suplys',    amount: 412.55,   status: 'flagged',
      signal: 'IBAN typosquat · duplicate amount' },
    { id: '4', time: '14:03:55', merchant: 'Cloud Hosting Co',         amount: 2400.00,  status: 'pending',
      signal: 'first payment to supplier' },
    { id: '5', time: '14:04:31', merchant: 'Payroll · April batch 2',  amount: 18234.10, status: 'held',
      signal: 'off-hours payroll' },
  ];

  onReview(tx: DemoTx) {
    this.toast.show(
      `Reviewing ${tx.merchant} (${tx.status})`,
      tx.status === 'flagged' ? 'error' : 'info',
    );
  }
}
