import {Component, inject, OnDestroy, OnInit} from '@angular/core';
import {HomeLoaderService, UpdatesState} from '../home-loader.service';
import {Subscription} from 'rxjs';
import {ActivatedRoute, Router, RouterOutlet} from '@angular/router';
import {UpdatePreviewBoxComponent} from '../update-preview-box/update-preview-box.component';
import {SearchBarComponent} from '../search-bar/search-bar.component';

@Component({
  selector: 'app-home-view',
  imports: [
    RouterOutlet,
    UpdatePreviewBoxComponent,
    SearchBarComponent
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
    if (!this.homeLoaderService.isLoaded()) this.homeLoaderService.startFetchingUpdates();
    this.updatesSubscription = this.homeLoaderService
      .updates$
      .subscribe((fetchingResult: UpdatesState | null) => {
        this.displayedUpdates = fetchingResult;
      });
    this.isDefaultView = this.activatedRoute.children.length === 0;
  }

  constructor(private router: Router, private activatedRoute: ActivatedRoute) {
  }

  ngOnDestroy(): void {
    this.updatesSubscription.unsubscribe();
  }

}
