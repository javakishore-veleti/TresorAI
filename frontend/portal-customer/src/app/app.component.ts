import { Component } from '@angular/core';
import { RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';
import { TaiToastHostComponent } from './primitives';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, RouterLink, RouterLinkActive, TaiToastHostComponent],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css',
})
export class AppComponent {
  navItems = [
    { path: '/stream',   label: 'Stream',   description: 'Live AP transactions' },
    { path: '/forecast', label: 'Forecast', description: '30 / 60 / 90 day cash' },
    { path: '/agent',    label: 'Agent',    description: 'Reasoning trace + ask' },
    { path: '/flagged',  label: 'Flagged',  description: 'Hold / Release / Alert' },
  ];
}
