import { Component } from '@angular/core';
import { TaiAlertComponent, TaiStatusPillComponent } from '../primitives';

@Component({
  selector: 'tai-agent-page',
  standalone: true,
  imports: [TaiAlertComponent, TaiStatusPillComponent],
  template: `
    <header class="mb-6">
      <h1 class="text-3xl font-semibold text-forest tracking-tight">Agent reasoning trace</h1>
      <p class="mt-1 text-bronze">
        See exactly how the agent reached its recommendation — every tool call, every citation.
        <span class="font-mono text-xs text-mauve ml-2">[T17 — Gemini 2.0 Flash + tool use]</span>
      </p>
    </header>

    <tai-alert variant="info" class="mb-6 block">
      Live trace will stream from intelligence-service /agent/judge once T15/T17 land. The shape below is the contract.
    </tai-alert>

    <!-- Demo trace card -->
    <div class="rounded-tai border border-sand bg-surface-elevated shadow-tai-card overflow-hidden">
      <div class="flex items-center justify-between border-b border-sand px-5 py-4 bg-surface-cream">
        <div>
          <div class="text-sm text-bronze">Transaction</div>
          <div class="font-semibold text-forest">A.C.M.E Office Suplys · $412.55</div>
        </div>
        <tai-status-pill status="flagged">flagged</tai-status-pill>
      </div>

      <ol class="divide-y divide-sand">
        @for (step of demoTrace; track $index) {
          <li class="px-5 py-4 flex gap-4">
            <span class="font-mono text-xs text-bronze w-8 pt-0.5 shrink-0">{{ $index + 1 }}</span>
            <div class="flex-1">
              <div class="flex items-center gap-2">
                <span class="font-mono text-xs uppercase tracking-wide font-semibold text-mauve">
                  {{ step.kind }}
                </span>
                <span class="text-sm text-forest">{{ step.text }}</span>
              </div>
              @if (step.citation) {
                <div class="mt-1 ml-0 inline-block rounded-tai-sm bg-surface-cream border border-sand px-2 py-1 text-xs font-mono text-bronze">
                  cite: {{ step.citation }}
                </div>
              }
            </div>
          </li>
        }
      </ol>

      <div class="border-t border-sand px-5 py-4 bg-surface-cream">
        <div class="text-xs uppercase tracking-wide text-bronze font-medium">Agent decision</div>
        <div class="mt-1 text-forest font-medium">
          Hold — likely supplier-name typosquat duplicate of ACME Office Supplies (paid 4 mins ago).
        </div>
      </div>
    </div>
  `,
})
export class AgentPageComponent {
  demoTrace = [
    { kind: 'tool', text: 'get_supplier_history(\'A.C.M.E Office Suplys\')',
      citation: 'no exact match in supplier corpus' },
    { kind: 'tool', text: 'get_similar_past_tx(merchant_embedding, k=3)',
      citation: 'tx_88421 · ACME Office Supplies · $412.55 · 4m ago' },
    { kind: 'reasoning', text: 'Vendor name diverges by 4 chars from a known supplier paid in the last 5 minutes for the same exact amount. High-confidence typosquat duplicate.' },
    { kind: 'tool', text: 'get_cash_position()',
      citation: 'cash 30d: $214,820' },
    { kind: 'reasoning', text: 'Holding does not cause cash issue. Recommend: Hold for human review.' },
  ];
}
