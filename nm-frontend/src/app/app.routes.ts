import { Routes } from '@angular/router';
import {NotFoundComponent} from './not-found/not-found.component';
import {LogInComponent} from './log-in/log-in.component';

export const LOG_IN_ROUTE = '/log-in';
export const NOT_FOUND_ROUTE = '*';
export const HOME_ROUTE = '/home';

export const routes: Routes = [
  {path: '', redirectTo: '/log-in', pathMatch: 'full'},
  {path: '/log-in', component: LogInComponent, pathMatch: 'full'},
  {path: '*', component: NotFoundComponent, pathMatch: 'full'}
];
