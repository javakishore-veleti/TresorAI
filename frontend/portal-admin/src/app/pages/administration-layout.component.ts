import { Component } from '@angular/core';
import { RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';
import { NgClass } from '@angular/common';

interface LeftNavGroup {
  label: string;
  items: { path: string; label: string }[];
}

@Component({
  selector: 'tai-administration-layout',
  standalone: true,
  imports: [RouterOutlet, RouterLink, RouterLinkActive, NgClass],
  template: `
    <!-- Left nav -->
    <aside class="w-60 shrink-0 bg-surface-elevated border-r border-sand">
      <div class="p-5 border-b border-sand">
        <div class="text-xs uppercase tracking-wide text-bronze font-semibold">Administration</div>
        <div class="mt-1 text-sm text-bronze">Install + ops machinery</div>
      </div>
      <nav class="py-3">
        @for (g of groups; track g.label) {
          <div class="px-5 pt-3 pb-1 text-[11px] uppercase tracking-wide text-bronze font-semibold">
            {{ g.label }}
          </div>
          @for (it of g.items; track it.path) {
            <a
              [routerLink]="it.path"
              routerLinkActive="bg-surface-cream border-l-brand-emerald-700 text-forest"
              #rla="routerLinkActive"
              class="flex items-center px-5 py-2 text-sm border-l-2 border-l-transparent transition-colors"
              [ngClass]="rla.isActive ? '' : 'text-bronze hover:text-forest hover:bg-surface-cream'"
            >
              {{ it.label }}
            </a>
          }
        }
      </nav>
    </aside>

    <!-- Content area -->
    <section class="flex-1 px-8 py-8 overflow-x-auto">
      <router-outlet />
    </section>
  `,
})
export class AdministrationLayoutComponent {
  groups: LeftNavGroup[] = [
    {
      label: 'Data Management',
      items: [
        { path: 'data-management/initial-downloads', label: 'Initial Downloads' },
        { path: 'data-management/reference-data',    label: 'Reference data' },
      ],
    },
    {
      label: 'Operations',
      items: [
        { path: 'users-and-roles', label: 'Users & Roles' },
        { path: 'agent-config',    label: 'Agent configuration' },
      ],
    },
  ];
}
