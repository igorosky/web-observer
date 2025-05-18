import {Injectable, OnDestroy} from '@angular/core';
import {HttpClient, HttpErrorResponse, HttpParams} from '@angular/common/http';
import {AuthData} from '../auth/models/auth-data';
import {UpdateEntry} from './models/site';
import {BehaviorSubject, catchError, interval, map, of, Subject, Subscription, takeUntil} from 'rxjs';
import {handleError, logAndExtractMessage} from '../shared/error-handling';

export interface UpdatesState {
  updates: UpdateEntry[] | null;
  errorMessage: string | null;
}

const UPDATES_POLL_INTERVAL_MS = 5000;

@Injectable({
  providedIn: 'root'
})
export class HomeLoaderService implements OnDestroy {
  private readonly baseUrl = 'http://localhost:8080';
  private readonly updatesSubject: BehaviorSubject<UpdatesState | null> = new BehaviorSubject<UpdatesState | null>(null);
  private destroy$ = new Subject<void>();
  private isFetchingUpdates: boolean = false;

  constructor(private http: HttpClient) {
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
    this.updatesSubject.complete(); //todo
    this.updatesSubject.unsubscribe();
  }

  isLoaded(): boolean {
    return this.isFetchingUpdates;
  }

  preloadHomeView(userData: AuthData) {
    this.startFetchingUpdates(userData);
  }

  startFetchingUpdates(userData: AuthData) {
    if (this.isFetchingUpdates) return;
    this.isFetchingUpdates = true;
    interval(UPDATES_POLL_INTERVAL_MS)
      .pipe(takeUntil(this.destroy$))
      .subscribe(() => {
        this.refetchUpdates(userData.username);
      });
  }


  private refetchUpdates(forUsername: string) {
    const params = new HttpParams();
    params.set('username', forUsername);
    this.http.get<UpdateEntry[]>(`${this.baseUrl}/updates`, {params: params})
      .pipe(
        map(updates => {
          return updates.length > 0 ? {updates: updates, errorMessage: null} : null;
        }),
        catchError((err: HttpErrorResponse) => {
          const message = logAndExtractMessage(err)
          return of({updates: null, errorMessage: message});
        })
      ).subscribe((value: UpdatesState | null) => this.updatesSubject.next(value))
  }

  get updates$() {
    return this.updatesSubject.asObservable();
  }

}
