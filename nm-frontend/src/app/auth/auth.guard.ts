import {Inject, Injectable, PLATFORM_ID} from '@angular/core';
import {CanActivate, Router} from '@angular/router';
import {isPlatformBrowser} from '@angular/common';
import {AuthService} from './auth.service';
import {Observable, of, tap} from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class AuthGuard implements CanActivate {
  constructor(@Inject(PLATFORM_ID) private platformId: object, private authService: AuthService, private router: Router) {
  }

  canActivate(): Observable<boolean> {
    if(isPlatformBrowser(this.platformId)){
      return this.authService.isLoggedIn().pipe(
        tap(status => {
          if (!status) {
            alert('You must be logged in to access this page.');
          }
        })
      )
    }
    return of(true);
  }
}
