import {Routes} from '@angular/router';
import {NotFoundComponent} from './not-found/not-found.component';
import {LogInComponent} from './log-in/log-in.component';
import {HomeViewComponent} from './home/home-view/home-view.component';
import {AuthGuard} from './auth/auth.guard';
import {SiteViewComponent} from './home/site-view/site-view.component';
import {SiteRegisterComponent} from './home/site-register/site-register.component';

export const LOG_IN_ROUTE = 'log-in';
export const NOT_FOUND_ROUTE = '**';
export const HOME_ROUTE = 'home';
export const SITE_ROUTE = 'site/:site_id'
export const SITE_REGISTER_ROUTE = 'register';

export const routes: Routes = [
  {path: '', redirectTo: LOG_IN_ROUTE, pathMatch: 'full'},
  {path: LOG_IN_ROUTE, component: LogInComponent, pathMatch: 'full'},
  {
    path: HOME_ROUTE, component: HomeViewComponent, canActivate: [AuthGuard],
    children: [
      {path: SITE_ROUTE, component: SiteViewComponent},
      {path: SITE_REGISTER_ROUTE, component: SiteRegisterComponent}
    ]
  },
  {path: NOT_FOUND_ROUTE, component: NotFoundComponent}
];
