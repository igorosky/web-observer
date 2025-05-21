import {Component, inject, OnDestroy, OnInit} from '@angular/core';
import {HomeLoaderService, UpdatesState} from '../home-loader.service';
import {Subscription} from 'rxjs';
import {AuthService} from '../../auth/auth.service';
import {Router, RouterOutlet} from '@angular/router';
import {UpdateEntryPreview} from '../models/site';
import {UpdatePreviewBoxComponent} from '../update-preview-box/update-preview-box.component';

@Component({
  selector: 'app-home-view',
  imports: [
    RouterOutlet,
    UpdatePreviewBoxComponent
  ],
  templateUrl: './home-view.component.html',
  styleUrl: './home-view.component.css',
  standalone: true
})
export class HomeViewComponent implements OnInit, OnDestroy {

  private authService: AuthService = inject(AuthService);
  private homeLoaderService: HomeLoaderService = inject(HomeLoaderService);
  private updatesSubscription!: Subscription;
  protected displayedUpdates: UpdatesState | null = null;

  ngOnInit(): void {
    if (!this.homeLoaderService.isLoaded()) {
      this.authService.getCurrentUserData().subscribe({
        next: (data) => {
          this.homeLoaderService.startFetchingUpdates(data);
        }
      });
    }
    this.updatesSubscription = this.homeLoaderService
      .updates$
      .subscribe((fetchingResult: UpdatesState | null) => {
        const update: UpdateEntryPreview = {
          siteId: "123",
          siteUrl: "https://test/url.com",
          siteName: "my site exists",
          registeredAt: "2025-01-01T00:00:00.000Z",
          statusCode: 200
        }
        const nonExistUpdate: UpdateEntryPreview = {
          siteId: "124",
          siteUrl: "https://test/url.com",
          siteName: "my site doesn't exist",
          registeredAt: "2025-01-01T00:00:00.000Z",
          statusCode: 503
        }
        const nonExistent2: UpdateEntryPreview = {
          siteId: "125",
          siteUrl: "https://test2/url.com",
          siteName: "my site doesn't exist2",
          registeredAt: "2025-01-01T00:00:00.000Z",
          statusCode: 401
        }
        let dummyUpdates: UpdatesState = {
          errorMessage: null,
          updates: []
        }
        for (let i = 0; i < 3; i++) {
          dummyUpdates.updates!.push(update); //todo
          dummyUpdates.updates!.push(nonExistUpdate);
          dummyUpdates.updates!.push(nonExistent2);
        }
        dummyUpdates.updates!.push(nonExistUpdate);
        this.displayedUpdates = dummyUpdates;
      });
  }

  constructor(private router: Router) {
  }

  ngOnDestroy(): void {
    this.updatesSubscription.unsubscribe();
  }

}
