import {Component, inject, OnDestroy, OnInit} from '@angular/core';
import {HomeLoaderService, UpdatesState} from '../home-loader.service';
import {Subscription} from 'rxjs';
import {StorageService} from '../../auth/storage.service';
import {AuthService} from '../../auth/auth.service';
import {Router, RouterOutlet} from '@angular/router';
import {UpdateEntry} from '../models/site';
import {UpdateBoxComponent} from '../update-box/update-box.component';

@Component({
  selector: 'app-home-view',
  imports: [
    RouterOutlet,
    UpdateBoxComponent
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
        const dummyUpdates: UpdatesState = {
          errorMessage: null,
          updates: []
        }
        this.displayedUpdates = dummyUpdates;
      });
  }

  constructor(private router: Router) {
  }

  ngOnDestroy(): void {
    this.updatesSubscription.unsubscribe();
  }

}
