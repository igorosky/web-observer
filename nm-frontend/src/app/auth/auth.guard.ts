import {Inject, Injectable, PLATFORM_ID} from '@angular/core';
import {CanActivate, Router} from '@angular/router';
import {isPlatformBrowser} from '@angular/common';
import {AuthService} from './auth.service';
import {LOG_IN_ROUTE} from '../app.routes';

@Injectable({
  providedIn: 'root',
})
export class AuthGuard implements CanActivate {
  constructor(@Inject(PLATFORM_ID) private platformId: object, private authService: AuthService, private router: Router) {
  }

  canActivate(): boolean {
    if (isPlatformBrowser(this.platformId)) {
      if (this.authService.isLoggedIn()) return true;
      alert('You must be logged in to access this page.');
      void this.router.navigate([LOG_IN_ROUTE]);
      return false;
    }
    return true;
  }
}
