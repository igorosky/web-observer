import { Injectable } from '@angular/core';
import {
  HttpEvent, HttpInterceptor, HttpHandler, HttpRequest, HTTP_INTERCEPTORS
} from '@angular/common/http';
import { Observable } from 'rxjs';
import {CookieInterceptor} from '@app/interceptors/cookie.interceptor';

@Injectable()
export class CsrfInterceptor implements HttpInterceptor {
  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    if (req.method !== 'GET' && req.method !== 'HEAD') {
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

export const csrfInterceptor = [
  {provide: HTTP_INTERCEPTORS, useClass: CsrfInterceptor, multi: true},
];
