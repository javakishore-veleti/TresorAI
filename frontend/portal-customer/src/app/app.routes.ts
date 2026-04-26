import { Routes } from '@angular/router';

export const routes: Routes = [
  { path: '', pathMatch: 'full', redirectTo: 'stream' },
  {
    path: 'stream',
    loadComponent: () => import('./pages/stream.page').then(m => m.StreamPageComponent),
    title: 'Live stream · TrésorAI',
  },
  {
    path: 'forecast',
    loadComponent: () => import('./pages/forecast.page').then(m => m.ForecastPageComponent),
    title: 'Cash-flow forecast · TrésorAI',
  },
  {
    path: 'agent',
    loadComponent: () => import('./pages/agent.page').then(m => m.AgentPageComponent),
    title: 'Agent reasoning · TrésorAI',
  },
  {
    path: 'flagged',
    loadComponent: () => import('./pages/flagged.page').then(m => m.FlaggedPageComponent),
    title: 'Flagged transactions · TrésorAI',
  },
  { path: '**', redirectTo: 'stream' },
];
