import {RenderMode, ServerRoute} from '@angular/ssr';
import {GOTIFY_ROUTE, HOME_ROUTE, LOG_IN_ROUTE, NOT_FOUND_ROUTE, SITE_REGISTER_ROUTE, SITE_ROUTE} from './app.routes';

export const serverRoutes: ServerRoute[] = [
  {
    path: LOG_IN_ROUTE,
    renderMode: RenderMode.Prerender
  },
  {
    path: NOT_FOUND_ROUTE,
    renderMode: RenderMode.Prerender
  },
  {
    path: `${HOME_ROUTE}/${SITE_REGISTER_ROUTE}`,
    renderMode: RenderMode.Prerender
  },
  {
    path: `${HOME_ROUTE}/${SITE_ROUTE}`,
    renderMode: RenderMode.Client
  },
  {
    path: `${HOME_ROUTE}/${GOTIFY_ROUTE}`,
    renderMode: RenderMode.Client
  },
  {
    path: HOME_ROUTE,
    renderMode: RenderMode.Server
  },
]
