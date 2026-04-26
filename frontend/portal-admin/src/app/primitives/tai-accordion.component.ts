import { Component, Input, signal } from '@angular/core';
import { NgClass } from '@angular/common';

@Component({
  selector: 'tai-accordion',
  standalone: true,
  imports: [NgClass],
  template: `
    <div class="rounded-tai border border-sand bg-surface-elevated overflow-hidden shadow-tai-card">
      <button
        type="button"
        class="w-full flex items-center justify-between px-5 py-4 text-left hover:bg-surface-cream transition-colors"
        [attr.aria-expanded]="open()"
        (click)="toggle()"
      >
        <div class="flex flex-col gap-0.5">
          <span class="font-semibold text-forest">{{ title }}</span>
          @if (subtitle) {
            <span class="text-sm text-bronze">{{ subtitle }}</span>
          }
        </div>
        <span
          class="ml-4 transition-transform text-bronze inline-block"
          [ngClass]="open() ? 'rotate-90' : ''"
          aria-hidden="true"
        >▶</span>
      </button>
      @if (open()) {
        <div class="border-t border-sand px-5 py-5">
          <ng-content />
        </div>
      }
    </div>
  `,
})
export class TaiAccordionComponent {
  @Input() title = '';
  @Input() subtitle = '';
  @Input() set initialOpen(v: boolean) { this.open.set(v); }

  open = signal(false);

  toggle() {
    this.open.update(v => !v);
  }
}
