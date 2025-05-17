import {Inject, Injectable, PLATFORM_ID} from '@angular/core';
import {CanActivate} from '@angular/router';
import {isPlatformBrowser} from '@angular/common';
import {AuthService} from './auth.service';

@Injectable({
  providedIn: 'root',
})
export class AuthGuard implements CanActivate {
  constructor(@Inject(PLATFORM_ID) private platformId: object, private authService: AuthService) {
  }

  canActivate(): boolean {
    if (isPlatformBrowser(this.platformId)) {
      if (this.authService.isLoggedIn()) return true;
      alert('You must be logged in to access this page.');
      return false;
    }
    return true;
  }
}
