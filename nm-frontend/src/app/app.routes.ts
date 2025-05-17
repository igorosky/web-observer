import { Routes } from '@angular/router';
import {NotFoundComponent} from './not-found/not-found.component';
import {LogInComponent} from './log-in/log-in.component';

export const routes: Routes = [
  {path: '', redirectTo: '/log-in', pathMatch: 'full'},
  {path: '/log-in', component: LogInComponent, pathMatch: 'full'},
  {path: '*', component: NotFoundComponent, pathMatch: 'full'}
];
