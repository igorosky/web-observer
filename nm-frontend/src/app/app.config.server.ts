import {ApplicationConfig, mergeApplicationConfig} from '@angular/core';
import {provideServerRendering} from '@angular/platform-server';
import {appConfig} from './app.config';
import {provideServerRouting, withAppShell} from '@angular/ssr';
import {serverRoutes} from '@app/app.routes.server';
import {HomeViewComponent} from '@app/home/home-view/home-view.component';

const serverConfig: ApplicationConfig = {
  providers: [
    provideServerRendering(),
    provideServerRouting(serverRoutes, withAppShell(HomeViewComponent)),
  ]
};

export const config = mergeApplicationConfig(appConfig, serverConfig);
