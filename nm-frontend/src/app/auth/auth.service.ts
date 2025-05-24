import {Injectable} from '@angular/core';
import {catchError, from, map, Observable, of, switchMap, tap, throwError} from 'rxjs';
import {LogInDto, LogInResponse} from './models/log-in-dto';
import {HttpClient} from '@angular/common/http';
import {StorageService} from './storage.service';
import {handleError, convertMessageToError} from '../shared/error-handling';
import {AuthData} from './models/auth-data';
import {LOG_IN_ROUTE} from '../app.routes';
import {Router} from '@angular/router';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private readonly baseUrl = 'http://localhost:8080';

  constructor(private http: HttpClient, private storageService: StorageService, private router: Router) {
  }

  isLoggedIn(): boolean {
    return this.storageService.isAuthDataSet();
  }

  attemptLogIn(logInData: LogInDto): Observable<AuthData> {
    return this.http.post<LogInResponse>(`${this.baseUrl}/login`, logInData)
      .pipe(
        map((response: LogInResponse): AuthData => {
          return {
            ...response,
            email: logInData.email
          } as AuthData;
        }),
        switchMap(authData => {
          if (!this.storageService.setAuthData(authData)) {
            return from(this.attemptLogOut(false)).pipe(
              switchMap(() => {
                if (this.storageService.setAuthData(authData)) return of(authData);
                else return throwError(() => new Error('Failed to save authentication data. Please clear local cache manually.'));
              })
            );
          }
          return of(authData);
        }),
        catchError(handleError)
      );
  }

  attemptLogOut(redirectToLogIn: boolean): Observable<void> {
    console.log('att')
    return this.http.post<void>(`${this.baseUrl}/logout`, null)
      .pipe(
        tap(() => {
          console.log('Logged out');
          this.storageService.clearOnLogOut();
          if(redirectToLogIn) this.redirectToLogIn();
        }),
        catchError(handleError)
      );
  }

  redirectToLogIn(): void {
    void this.router.navigate([LOG_IN_ROUTE]);
  }

  // noinspection JSUnusedGlobalSymbols
  getCurrentUserData(): Observable<AuthData> {
    const data = this.storageService.getAuthData();
    if(data === null){
      this.attemptLogOut(true);
      return convertMessageToError('User data was cleared during session. Please log in again.')
    }
    return of(data);
  }

}
