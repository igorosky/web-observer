import {Component, inject, OnDestroy, OnInit} from '@angular/core';
import {HomeLoaderService, UpdatesState} from '../home-loader.service';
import {Observable, Subscription} from 'rxjs';
import {ActivatedRoute, Router, RouterOutlet} from '@angular/router';
import {UpdatePreviewBoxComponent} from '../update-preview-box/update-preview-box.component';
import {SearchBarComponent} from '../search-bar/search-bar.component';
import {SitePreview} from '../models/site';
import {AuthService} from '../../auth/auth.service';
import {HOME_ROUTE, SITE_REGISTER_ROUTE} from '../../app.routes';

@Component({
  selector: 'app-home-view',
  imports: [
    RouterOutlet,
    UpdatePreviewBoxComponent,
    SearchBarComponent,
  ],
  templateUrl: './home-view.component.html',
  styleUrl: './home-view.component.css',
  standalone: true
})
export class HomeViewComponent implements OnInit, OnDestroy {

  private homeLoaderService: HomeLoaderService = inject(HomeLoaderService);
  private updatesSubscription!: Subscription;
  protected displayedUpdates: UpdatesState | null = null;
  protected isDefaultView = true;

  ngOnInit(): void {
    this.isDefaultView = this.activatedRoute.children.length === 0;
    if (!this.homeLoaderService.isLoaded()) this.homeLoaderService.startFetchingUpdates();
    this.updatesSubscription = this.homeLoaderService
      .updates$
      .subscribe((fetchingResult: UpdatesState | null) => {
        this.displayedUpdates = fetchingResult;
      });
  }

  constructor(private router: Router, private activatedRoute: ActivatedRoute, private authService: AuthService) {
  }

  ngOnDestroy(): void {
    this.updatesSubscription.unsubscribe();
  }

  fetchAvailableSites(): Observable<SitePreview[]> {
    return this.homeLoaderService.fetchUserSiteCollection();
  }

  onSearchSiteSelect(site: SitePreview) {
    this.isDefaultView = false;
    void this.router.navigate(['site', site.siteId], {relativeTo: this.activatedRoute});
  }

  attemptLogOut() {
    this.authService.attemptLogOut(true);
  }

  routeToRegisterSite() {
    this.isDefaultView = false;
    void this.router.navigate([SITE_REGISTER_ROUTE], {relativeTo: this.activatedRoute});
  }

  navigateToHome() {
    this.isDefaultView = true;
    void this.router.navigate([HOME_ROUTE]);
  }
}
