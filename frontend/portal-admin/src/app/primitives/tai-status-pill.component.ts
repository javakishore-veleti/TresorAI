import { Component, Input } from '@angular/core';
import { NgClass } from '@angular/common';

export type Status = 'released' | 'pending' | 'held' | 'flagged' | 'info';

@Component({
  selector: 'tai-status-pill',
  standalone: true,
  imports: [NgClass],
  template: `
    <span
      class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium border"
      [ngClass]="pillClass()"
    >
      <span class="size-1.5 rounded-full" [ngClass]="dotClass()"></span>
      <ng-content />
    </span>
  `,
})
export class TaiStatusPillComponent {
  @Input() status: Status = 'info';

  pillClass() {
    switch (this.status) {
      case 'released': return 'bg-surface-cream text-forest border-mint';
      case 'pending':  return 'bg-surface-cream text-forest border-amber';
      case 'held':     return 'bg-surface-cream text-forest border-mauve';
      case 'flagged':  return 'bg-coral-bg text-forest border-coral';
      default:         return 'bg-surface-cream text-forest border-sky';
    }
  }

  dotClass() {
    switch (this.status) {
      case 'released': return 'bg-mint';
      case 'pending':  return 'bg-amber';
      case 'held':     return 'bg-mauve';
      case 'flagged':  return 'bg-coral';
      default:         return 'bg-sky';
    }
  }
}
