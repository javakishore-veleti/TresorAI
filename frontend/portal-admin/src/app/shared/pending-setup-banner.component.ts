import { Component, inject } from '@angular/core';
import { RouterLink } from '@angular/router';
import { DecimalPipe } from '@angular/common';
import { PendingSetupService } from './pending-setup.service';

@Component({
  selector: 'tai-pending-setup-banner',
  standalone: true,
  imports: [RouterLink, DecimalPipe],
  template: `
    @if (svc.hasPending()) {
      <div class="bg-surface-cream border-b-2 border-amber" role="alert">
        <div class="max-w-screen-2xl mx-auto px-6 py-3 flex items-center gap-4">
          <span class="font-mono text-xs uppercase tracking-wide font-semibold text-bronze shrink-0">
            Setup pending
          </span>
          <span class="text-sm text-forest flex-1">
            <strong>{{ svc.pending().length }} datasets</strong>
            ({{ svc.requiredPendingCount() }} required, ~{{ svc.totalPendingGb() | number:'1.0-1' }} GB)
            not yet loaded on this install.
            <span class="text-bronze">Loads run via Airflow — initiate from the page below.</span>
          </span>
          <a
            routerLink="/administration/data-management/initial-downloads"
            class="shrink-0 px-3 py-1.5 rounded-tai-sm text-sm font-medium bg-brand-emerald-700 text-surface-pearl hover:bg-brand-emerald-500 transition-colors"
          >
            Open Initial Downloads →
          </a>
        </div>
      </div>
    }
  `,
})
export class PendingSetupBannerComponent {
  svc = inject(PendingSetupService);
}
