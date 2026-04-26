import { Injectable, signal } from '@angular/core';

export type ToastVariant = 'info' | 'success' | 'warning' | 'error';

export interface Toast {
  id: number;
  message: string;
  variant: ToastVariant;
}

@Injectable({ providedIn: 'root' })
export class TaiToastService {
  private nextId = 1;
  toasts = signal<Toast[]>([]);

  show(message: string, variant: ToastVariant = 'info', ttl = 4000) {
    const id = this.nextId++;
    this.toasts.update(arr => [...arr, { id, message, variant }]);
    if (ttl > 0) {
      setTimeout(() => this.dismiss(id), ttl);
    }
  }

  dismiss(id: number) {
    this.toasts.update(arr => arr.filter(t => t.id !== id));
  }
}
