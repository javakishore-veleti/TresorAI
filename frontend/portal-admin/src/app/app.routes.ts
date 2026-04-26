import { Routes } from '@angular/router';

export const routes: Routes = [
  { path: '', pathMatch: 'full', redirectTo: 'administration' },
  {
    path: 'administration',
    loadComponent: () =>
      import('./pages/administration-layout.component').then(m => m.AdministrationLayoutComponent),
    children: [
      { path: '', pathMatch: 'full', redirectTo: 'data-management/initial-downloads' },
      {
        path: 'data-management/initial-downloads',
        loadComponent: () =>
          import('./pages/initial-downloads.page').then(m => m.InitialDownloadsPageComponent),
        title: 'Initial Downloads · TrésorAI Admin',
      },
      {
        path: 'data-management/reference-data',
        loadComponent: () =>
          import('./pages/placeholder.page').then(m => m.PlaceholderPageComponent),
        data: { heading: 'Reference data', subtitle: 'Sanctions lists, country codes, IBAN typosquat lookups' },
        title: 'Reference data · TrésorAI Admin',
      },
      {
        path: 'users-and-roles',
        loadComponent: () =>
          import('./pages/placeholder.page').then(m => m.PlaceholderPageComponent),
        data: { heading: 'Users & Roles', subtitle: 'IAM, role assignments, audit of access changes' },
        title: 'Users & Roles · TrésorAI Admin',
      },
      {
        path: 'agent-config',
        loadComponent: () =>
          import('./pages/placeholder.page').then(m => m.PlaceholderPageComponent),
        data: { heading: 'Agent configuration', subtitle: 'Thresholds, tools, prompt overrides' },
        title: 'Agent config · TrésorAI Admin',
      },
    ],
  },
  {
    path: 'tenants',
    loadComponent: () =>
      import('./pages/placeholder.page').then(m => m.PlaceholderPageComponent),
    data: { heading: 'Tenants', subtitle: 'Multi-tenant customer management' },
    title: 'Tenants · TrésorAI Admin',
  },
  {
    path: 'models',
    loadComponent: () =>
      import('./pages/placeholder.page').then(m => m.PlaceholderPageComponent),
    data: { heading: 'Models', subtitle: 'False-positive / negative rate, latency, decision audit' },
    title: 'Models · TrésorAI Admin',
  },
  {
    path: 'system',
    loadComponent: () =>
      import('./pages/system-health.page').then(m => m.SystemHealthPageComponent),
    title: 'System Health · TrésorAI Admin',
  },
  { path: '**', redirectTo: 'administration' },
];
