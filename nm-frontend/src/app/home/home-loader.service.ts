import {Injectable, OnDestroy} from '@angular/core';
import {HttpClient, HttpErrorResponse, HttpParams} from '@angular/common/http';
import {AuthData} from '../auth/models/auth-data';
import {SiteDetails, UpdateEntryPreview} from './models/site';
import {BehaviorSubject, catchError, interval, map, Observable, of, Subject, takeUntil} from 'rxjs';
import {handleError, logAndExtractMessage} from '../shared/error-handling';

export interface UpdatesState {
  updates: UpdateEntryPreview[] | null;
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
    const params = new HttpParams().set('username', forUsername);
    this.http.get<UpdateEntryPreview[]>(`${this.baseUrl}/updates`, {params: params})
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

  fetchSiteInfo(siteId: string): Observable<SiteDetails> {
    const params = new HttpParams().set('siteId', siteId);
    return this.http.get<SiteDetails>(`${this.baseUrl}/site`, {params: params})
      .pipe(catchError(handleError));
  }

  removeSite(siteId: string): Observable<void> {
    const params = new HttpParams().set('siteId', siteId);
    return this.http.delete<void>(`${this.baseUrl}/site`, {params: params}).pipe(catchError(handleError));
  }

  editSite(siteEditData: FormData): Observable<void> {
    return this.http.patch<void>(`${this.baseUrl}/site`, siteEditData).pipe(catchError(handleError));
  }

}
