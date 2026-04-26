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
      <div class="bg-coral-bg border-y-2 border-coral" role="alert" aria-live="polite">
        <div class="max-w-screen-2xl mx-auto px-6 py-3 flex items-start gap-4">
          <span
            class="size-2.5 rounded-full bg-coral shrink-0 mt-1.5 animate-pulse"
            aria-hidden="true"
          ></span>

          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-3 flex-wrap">
              <span class="font-mono text-xs uppercase tracking-wider font-bold text-coral">
                Initial setup required
              </span>
              <span class="text-sm text-forest">
                <strong>{{ svc.pending().length }} datasets</strong>
                ({{ svc.requiredPendingCount() }} required, ~{{ svc.totalPendingGb() | number:'1.0-1' }} GB)
                must be loaded before this install is operational.
              </span>
            </div>

            <details class="mt-1.5">
              <summary class="text-xs text-bronze cursor-pointer hover:text-forest transition-colors select-none">
                What's missing? ({{ svc.pending().length }} datasets)
              </summary>
              <ul class="mt-2 text-xs text-forest space-y-1 pl-4 list-disc">
                @for (d of svc.pending(); track d.key) {
                  <li>
                    <span class="font-medium">{{ d.title }}</span>
                    @if (d.required) {
                      <span class="ml-2 inline-flex items-center px-1.5 py-0.5 rounded-tai-sm bg-coral text-surface-pearl text-[10px] font-mono uppercase tracking-wide">
                        required
                      </span>
                    } @else {
                      <span class="ml-2 inline-flex items-center px-1.5 py-0.5 rounded-tai-sm bg-surface-cream text-bronze text-[10px] font-mono uppercase tracking-wide border border-sand">
                        optional
                      </span>
                    }
                  </li>
                }
              </ul>
            </details>
          </div>

          <a
            routerLink="/administration/data-management/initial-downloads"
            class="shrink-0 px-4 py-2 rounded-tai-sm text-sm font-semibold bg-coral text-surface-pearl hover:opacity-90 transition-opacity shadow-tai-card whitespace-nowrap"
          >
            Run Initial Downloads →
          </a>
        </div>
      </div>
    }
  `,
})
export class PendingSetupBannerComponent {
  svc = inject(PendingSetupService);
}
