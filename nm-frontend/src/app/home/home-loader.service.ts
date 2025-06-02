import {Injectable, OnDestroy} from '@angular/core';
import {HttpClient, HttpErrorResponse, HttpParams} from '@angular/common/http';
import {BareUpdateEntry, SiteDetails, SitePreview, UpdateEntryPreview} from './models/site';
import {BehaviorSubject, catchError, interval, map, Observable, of, Subject, takeUntil} from 'rxjs';
import {handleError, logAndExtractMessage} from '../shared/error-handling';

export interface UpdatesState {
  updates: UpdateEntryPreview[] | null;
  errorMessage: string | null;
}

export interface SiteRegisterResponse{
  siteId: string;
}

const UPDATES_POLL_INTERVAL_MS = 15000;

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
    this.updatesSubject.complete();
    this.updatesSubject.unsubscribe();
  }

  isLoaded(): boolean {
    return this.isFetchingUpdates;
  }

  preloadHomeView() {
    this.startFetchingUpdates();
  }

  startFetchingUpdates() {
    if (this.isFetchingUpdates) return;
    this.isFetchingUpdates = true;
    interval(UPDATES_POLL_INTERVAL_MS)
      .pipe(takeUntil(this.destroy$))
      .subscribe(() => {
        this.refetchUpdates();
      });
  }


  private refetchUpdates() {
    this.http.get<UpdateEntryPreview[]>(`${this.baseUrl}/updates`)
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

  fetchSiteUpdates(siteId: string): Observable<BareUpdateEntry[]> {
    const params = new HttpParams().set('siteId', siteId).set('onlyUpdates', 'true');
    return this.http.get<BareUpdateEntry[]>(`${this.baseUrl}/site`, {params: params})
      .pipe(catchError(handleError));
  }

  removeSite(siteId: string): Observable<void> {
    const params = new HttpParams().set('siteId', siteId);
    return this.http.delete<void>(`${this.baseUrl}/site`, {params: params}).pipe(catchError(handleError));
  }

  editSite(siteEditData: FormData): Observable<void> {
    return this.http.patch<void>(`${this.baseUrl}/site`, siteEditData).pipe(catchError(handleError));
  }

  registerSite(siteRegisterData: FormData): Observable<SiteRegisterResponse> {
    return this.http.post<SiteRegisterResponse>(`${this.baseUrl}/site`, siteRegisterData).pipe(catchError(handleError));
  }

  fetchUserSiteCollection(): Observable<SitePreview[]> {
    return this.http.get<SitePreview[]>(`${this.baseUrl}/collection`)
      .pipe(catchError(handleError));
  }
}
