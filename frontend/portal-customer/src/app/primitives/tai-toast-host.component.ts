import { Component, inject } from '@angular/core';
import { NgClass } from '@angular/common';
import { TaiToastService, ToastVariant } from './tai-toast.service';

@Component({
  selector: 'tai-toast-host',
  standalone: true,
  imports: [NgClass],
  template: `
    <div
      class="fixed top-4 right-4 z-50 flex flex-col gap-2 pointer-events-none"
      aria-live="polite"
      aria-atomic="true"
    >
      @for (t of svc.toasts(); track t.id) {
        <div
          class="pointer-events-auto rounded-tai border-2 px-4 py-3 shadow-tai-elevated bg-surface-elevated min-w-72 max-w-md flex items-start gap-3"
          [ngClass]="borderClass(t.variant)"
        >
          <span class="font-mono text-xs uppercase tracking-wide pt-0.5 font-semibold text-forest">
            {{ t.variant.toUpperCase() }}
          </span>
          <span class="flex-1 text-sm text-forest">{{ t.message }}</span>
          <button
            type="button"
            class="text-bronze hover:text-forest text-base leading-none"
            (click)="svc.dismiss(t.id)"
            aria-label="Dismiss"
          >×</button>
        </div>
      }
    </div>
  `,
})
export class TaiToastHostComponent {
  svc = inject(TaiToastService);

  borderClass(variant: ToastVariant): string {
    switch (variant) {
      case 'success': return 'border-mint';
      case 'warning': return 'border-amber';
      case 'error':   return 'border-coral';
      default:        return 'border-sky';
    }
  }
}
