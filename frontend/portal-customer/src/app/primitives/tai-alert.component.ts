import { Component, Input } from '@angular/core';
import { NgClass } from '@angular/common';

export type AlertVariant = 'info' | 'success' | 'warning' | 'error';

@Component({
  selector: 'tai-alert',
  standalone: true,
  imports: [NgClass],
  template: `
    <div
      role="alert"
      class="rounded-tai border px-4 py-3 flex items-start gap-3"
      [ngClass]="containerClass()"
    >
      <span class="font-mono text-xs uppercase tracking-wide pt-0.5 font-semibold">
        {{ variant.toUpperCase() }}
      </span>
      <div class="flex-1 text-sm leading-relaxed text-forest">
        <ng-content />
      </div>
    </div>
  `,
})
export class TaiAlertComponent {
  @Input() variant: AlertVariant = 'info';

  containerClass() {
    switch (this.variant) {
      case 'success': return 'bg-surface-cream border-mint';
      case 'warning': return 'bg-surface-cream border-amber';
      case 'error':   return 'bg-coral-bg border-coral';
      default:        return 'bg-surface-cream border-sky';
    }
  }
}
