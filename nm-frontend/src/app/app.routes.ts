import { Routes } from '@angular/router';
import {NotFoundComponent} from './not-found/not-found.component';
import {LogInComponent} from './log-in/log-in.component';
import {HomeViewComponent} from './home/home-view/home-view.component';
import {AuthGuard} from './auth/auth.guard';

export const LOG_IN_ROUTE = 'log-in';
export const NOT_FOUND_ROUTE = '**';
export const HOME_ROUTE = 'home';

export const routes: Routes = [
  {path: '', redirectTo: LOG_IN_ROUTE, pathMatch: 'full'},
  {path: LOG_IN_ROUTE, component: LogInComponent, pathMatch: 'full'},
  {path: HOME_ROUTE, component: HomeViewComponent, pathMatch: 'full', canActivate: [AuthGuard]},
  {path: NOT_FOUND_ROUTE, component: NotFoundComponent}
];
