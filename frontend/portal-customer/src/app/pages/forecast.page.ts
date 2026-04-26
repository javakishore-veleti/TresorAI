import { Component } from '@angular/core';
import { TaiAlertComponent } from '../primitives';

@Component({
  selector: 'tai-forecast-page',
  standalone: true,
  imports: [TaiAlertComponent],
  template: `
    <header class="mb-6">
      <h1 class="text-3xl font-semibold text-forest tracking-tight">30 / 60 / 90 day cash-flow forecast</h1>
      <p class="mt-1 text-bronze">
        Projected position with confidence bands, updating as agent decisions land.
        <span class="font-mono text-xs text-mauve ml-2">[T19 — Prophet + LLM-derived adjustments]</span>
      </p>
    </header>

    <tai-alert variant="info" class="mb-6 block">
      Forecast endpoint not wired yet. Lands when intelligence-service is scaffolded at T06 and the forecast view is built at T19.
    </tai-alert>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      @for (h of horizons; track h.days) {
        <div class="rounded-tai border border-sand bg-surface-elevated shadow-tai-card p-5">
          <div class="text-xs uppercase tracking-wide text-bronze font-medium">{{ h.label }}</div>
          <div class="mt-2 text-2xl font-semibold text-forest font-mono">{{ h.preview }}</div>
          <div class="mt-1 text-xs text-bronze">confidence band placeholder</div>
        </div>
      }
    </div>

    <div class="mt-8 rounded-tai border border-dashed border-sand bg-surface-cream p-8 text-center text-bronze">
      <span class="font-mono text-xs">[chart area]</span>
      <p class="mt-2 text-sm">ECharts / Chart.js with confidence bands lands at T19.</p>
    </div>
  `,
})
export class ForecastPageComponent {
  horizons = [
    { days: 30, label: '30 days', preview: '$ —' },
    { days: 60, label: '60 days', preview: '$ —' },
    { days: 90, label: '90 days', preview: '$ —' },
  ];
}
