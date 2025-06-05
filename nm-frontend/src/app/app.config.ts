//app.config.ts
import {ApplicationConfig, provideZoneChangeDetection} from '@angular/core';
import {provideRouter} from '@angular/router';
import {provideServerRendering} from '@angular/platform-server';
import {provideServerRouting, withAppShell} from '@angular/ssr';
import {routes} from './app.routes';
import {provideHttpClient, withFetch, withInterceptorsFromDi, HTTP_INTERCEPTORS} from '@angular/common/http';
import {provideAnimations} from '@angular/platform-browser/animations';
import {cookieInterceptor} from './auth/cookie.interceptor';
import {CsrfInterceptor} from './interceptors/csrf.interceptor';
import {provideClientHydration, withEventReplay} from '@angular/platform-browser';
import {HomeViewComponent} from './home/home-view/home-view.component';
import {serverRoutes} from './app.routes.server';

export const appConfig: ApplicationConfig = {
  providers: [
    provideZoneChangeDetection({eventCoalescing: true}),
    provideClientHydration(withEventReplay()),
    provideRouter(routes),
    provideHttpClient(
      withFetch(),
      withInterceptorsFromDi(),
    ),
    provideAnimations(),
    provideServerRendering(),
    provideServerRouting(serverRoutes, withAppShell(HomeViewComponent)),
    cookieInterceptor,
    {
      provide: HTTP_INTERCEPTORS,
      useClass: CsrfInterceptor,
      multi: true
    }
  ]
};
