import {
  HTTP_INTERCEPTORS,
  HttpErrorResponse,
  HttpEvent,
  HttpHandler,
  HttpInterceptor,
  HttpRequest
} from '@angular/common/http';
import {Injectable} from '@angular/core';
import {catchError, Observable, throwError} from 'rxjs';
import {AuthService} from '../auth/auth.service';

@Injectable()
export class CookieInterceptor implements HttpInterceptor {

  constructor(private authService: AuthService) {}

  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    return next.handle(req.clone({withCredentials: true})).pipe(
      catchError(error => {
        if (error instanceof HttpErrorResponse){
          if(error.status === 403){
            this.authService.attemptLogOutNow(true);
            alert('Session expired, please log in again.');
          }
          if(error.status === 401) this.authService.redirectToLogIn();
        }
        return throwError(() => error)
      })
    )
  }
}

export const cookieInterceptor = [
  {provide: HTTP_INTERCEPTORS, useClass: CookieInterceptor, multi: true},
];
