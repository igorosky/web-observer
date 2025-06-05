// src/app/interceptors/csrf.interceptor.ts
import { Injectable } from '@angular/core';
import {
  HttpEvent, HttpInterceptor, HttpHandler, HttpRequest
} from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable()
export class CsrfInterceptor implements HttpInterceptor {
  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    // Sprawdź czy żądanie idzie do twojego API (backend)
    if (req.url.startsWith('http://localhost:8000') && req.method !== 'GET' && req.method !== 'HEAD') {
      const csrfToken = this.getCookie('csrftoken');
      if (csrfToken) {
        const modified = req.clone({
          withCredentials: true,
          setHeaders: {
            'X-CSRFToken': csrfToken
          }
        });
        return next.handle(modified);
      }
    }

    // GET i inne bez zmian
    return next.handle(req.clone({ withCredentials: true }));
  }

  private getCookie(name: string): string | null {
    const cookies = document.cookie.split(';');
    for (let c of cookies) {
      const [key, value] = c.trim().split('=');
      if (key === name) {
        return decodeURIComponent(value);
      }
    }
    return null;
  }
}
