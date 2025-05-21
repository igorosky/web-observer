import {Component, inject, OnDestroy, OnInit} from '@angular/core';
import {HomeLoaderService, UpdatesState} from '../home-loader.service';
import {Subscription} from 'rxjs';
import {AuthService} from '../../auth/auth.service';
import {Router, RouterOutlet} from '@angular/router';
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


  private homeLoaderService: HomeLoaderService = inject(HomeLoaderService);
  private updatesSubscription!: Subscription;
  protected displayedUpdates: UpdatesState | null = null;

  ngOnInit(): void {
    if (!this.homeLoaderService.isLoaded()) this.homeLoaderService.startFetchingUpdates();
    this.updatesSubscription = this.homeLoaderService
      .updates$
      .subscribe((fetchingResult: UpdatesState | null) => {
        this.displayedUpdates = fetchingResult;
      });
  }

  constructor(private router: Router) {
  }

  ngOnDestroy(): void {
    this.updatesSubscription.unsubscribe();
  }

}
