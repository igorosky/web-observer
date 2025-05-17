import { Routes } from '@angular/router';
import {NotFoundComponent} from './not-found/not-found.component';
import {LogInComponent} from './log-in/log-in.component';

export const LOG_IN_ROUTE = 'log-in';
export const NOT_FOUND_ROUTE = '**';
export const HOME_ROUTE = 'home';

export const routes: Routes = [
  {path: '', redirectTo: LOG_IN_ROUTE, pathMatch: 'full'},
  {path: LOG_IN_ROUTE, component: LogInComponent, pathMatch: 'full'},
  {path: NOT_FOUND_ROUTE, component: NotFoundComponent}
];
