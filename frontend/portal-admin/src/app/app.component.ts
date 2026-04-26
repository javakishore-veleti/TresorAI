import { Component } from '@angular/core';
import { RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';
import { TaiToastHostComponent } from './primitives';
import { PendingSetupBannerComponent } from './shared/pending-setup-banner.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, RouterLink, RouterLinkActive, TaiToastHostComponent, PendingSetupBannerComponent],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css',
})
export class AppComponent {
  topNav = [
    { path: '/administration', label: 'Administration' },
    { path: '/tenants',        label: 'Tenants' },
    { path: '/models',         label: 'Models' },
    { path: '/system',         label: 'System' },
  ];
}
