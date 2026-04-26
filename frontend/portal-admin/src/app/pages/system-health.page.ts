import { Component, OnDestroy, OnInit, inject, signal } from '@angular/core';
import { DatePipe } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Subscription, interval, startWith } from 'rxjs';

import { TaiAlertComponent, TaiStatusPillComponent } from '../primitives';

interface ServiceHealth {
  name: string;
  tier: 'frontend' | 'backend' | 'data' | 'messaging' | 'orchestration';
  target: string;
  status: 'up' | 'down' | 'unknown' | 'not_configured';
  latency_ms: number | null;
  detail: string | null;
}

interface SystemHealthResponse {
  environment: string;
  checked_at: string;
  services: ServiceHealth[];
}

const ADMIN_API = 'http://localhost:8091';
const POLL_MS = 5000;

const ENV_LABEL: Record<string, string> = {
  local:  'Local laptop',
  gcp:    'Google Cloud',
  aws:    'AWS',
  azure:  'Azure',
  hybrid: 'Hybrid',
};

@Component({
  selector: 'tai-system-health-page',
  standalone: true,
  imports: [DatePipe, TaiAlertComponent, TaiStatusPillComponent],
  host: { class: 'block w-full max-w-6xl mx-auto p-8' },
  template: `
    <header class="mb-6">
      <h1 class="text-3xl font-semibold text-forest tracking-tight">System Health</h1>
      <p class="mt-1 text-bronze">
        Live probe of every backend dependency from this <code class="font-mono text-mauve">admin-api</code> instance.
        Polls every {{ pollMs / 1000 }}s.
      </p>
    </header>

    @if (loadError()) {
      <tai-alert variant="error" class="mb-6 block">
        admin-api unreachable at {{ adminApiUrl }}: {{ loadError() }}.
      </tai-alert>
    } @else if (data()) {
      <!-- Environment summary -->
      <div class="mb-6 rounded-tai border border-sand bg-surface-elevated shadow-tai-card p-5 flex items-center justify-between flex-wrap gap-4">
        <div>
          <div class="text-xs uppercase tracking-wide text-bronze font-semibold">Deployment</div>
          <div class="mt-1 text-2xl font-semibold text-forest">{{ envLabel(data()!.environment) }}</div>
          <div class="text-xs text-bronze font-mono">TAI_ENV = {{ data()!.environment }}</div>
        </div>
        <div class="text-right">
          <div class="text-xs uppercase tracking-wide text-bronze font-semibold">Up · Down · Pending</div>
          <div class="mt-1 flex items-center gap-3 text-xl font-mono font-semibold">
            <span class="text-mint">{{ counts().up }}</span>
            <span class="text-bronze">·</span>
            <span class="text-coral">{{ counts().down }}</span>
            <span class="text-bronze">·</span>
            <span class="text-bronze">{{ counts().not_configured }}</span>
          </div>
          <div class="text-xs text-bronze">
            Last checked {{ data()!.checked_at | date:'mediumTime' }}
          </div>
        </div>
      </div>

      <!-- Services grouped by tier -->
      @for (tier of tiers(); track tier.tier) {
        <section class="mb-6">
          <h2 class="text-sm uppercase tracking-wide text-bronze font-semibold mb-2">{{ tier.tier }}</h2>
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            @for (s of tier.services; track s.name) {
              <div
                class="rounded-tai border bg-surface-elevated shadow-tai-card p-4"
                [class.border-mint]="s.status === 'up'"
                [class.border-coral]="s.status === 'down'"
                [class.border-sand]="s.status === 'not_configured'"
              >
                <div class="flex items-start justify-between gap-3 mb-2">
                  <div>
                    <div class="font-semibold text-forest">{{ s.name }}</div>
                    <code class="text-xs font-mono text-bronze break-all">{{ s.target || '— not configured —' }}</code>
                  </div>
                  <tai-status-pill [status]="pillFor(s.status)">{{ s.status }}</tai-status-pill>
                </div>
                <div class="flex items-center justify-between text-xs">
                  @if (s.latency_ms !== null) {
                    <span class="text-bronze font-mono">{{ s.latency_ms }} ms</span>
                  } @else {
                    <span class="text-bronze">—</span>
                  }
                  @if (s.detail) {
                    <span
                      class="text-bronze italic truncate ml-2"
                      [title]="s.detail"
                    >{{ s.detail }}</span>
                  }
                </div>
              </div>
            }
          </div>
        </section>
      }
    } @else {
      <div class="text-bronze italic">Loading…</div>
    }

    <footer class="mt-8 text-xs text-bronze font-mono">
      Configure overrides per environment via <code>TAI_ENV</code> + <code>TAI_SVC_&lt;name&gt;</code> env vars on the admin-api container.
    </footer>
  `,
})
export class SystemHealthPageComponent implements OnInit, OnDestroy {
  private http = inject(HttpClient);

  adminApiUrl = ADMIN_API;
  pollMs = POLL_MS;

  data = signal<SystemHealthResponse | null>(null);
  loadError = signal<string | null>(null);

  private sub?: Subscription;

  ngOnInit(): void {
    this.sub = interval(this.pollMs)
      .pipe(startWith(0))
      .subscribe(() => this.fetch());
  }

  ngOnDestroy(): void {
    this.sub?.unsubscribe();
  }

  fetch(): void {
    this.http
      .get<SystemHealthResponse>(`${ADMIN_API}/api/admin/system/health`)
      .subscribe({
        next: r => { this.data.set(r); this.loadError.set(null); },
        error: e => { this.loadError.set(e?.statusText || e?.message || 'connection refused'); },
      });
  }

  envLabel(env: string): string {
    return ENV_LABEL[env] ?? env;
  }

  counts() {
    const services = this.data()?.services ?? [];
    return {
      up: services.filter(s => s.status === 'up').length,
      down: services.filter(s => s.status === 'down').length,
      not_configured: services.filter(s => s.status === 'not_configured').length,
    };
  }

  tiers(): { tier: string; services: ServiceHealth[] }[] {
    const services = this.data()?.services ?? [];
    const order = ['frontend', 'backend', 'data', 'messaging', 'orchestration'];
    return order
      .map(t => ({ tier: t, services: services.filter(s => s.tier === t) }))
      .filter(g => g.services.length > 0);
  }

  pillFor(status: string): 'released' | 'pending' | 'held' | 'flagged' | 'info' {
    switch (status) {
      case 'up':              return 'released';
      case 'down':            return 'flagged';
      case 'not_configured':  return 'held';
      default:                return 'info';
    }
  }
}
