import { Component, inject } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { TaiAlertComponent } from '../primitives';

@Component({
  selector: 'tai-placeholder-page',
  standalone: true,
  imports: [TaiAlertComponent],
  host: { class: 'block w-full max-w-5xl' },
  template: `
    <header class="mb-6">
      <h1 class="text-3xl font-semibold text-forest tracking-tight">{{ heading }}</h1>
      @if (subtitle) {
        <p class="mt-1 text-bronze">{{ subtitle }}</p>
      }
    </header>

    <tai-alert variant="info">
      Placeholder page. Real implementation lands in a later milestone — see TresorAI_Portfolio_Build_Plan.xlsx.
    </tai-alert>
  `,
})
export class PlaceholderPageComponent {
  private route = inject(ActivatedRoute);

  heading: string = this.route.snapshot.data['heading'] ?? 'Section';
  subtitle: string = this.route.snapshot.data['subtitle'] ?? '';
}
