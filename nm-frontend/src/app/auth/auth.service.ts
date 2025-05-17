import {Injectable} from '@angular/core';
import {catchError, from, map, Observable, of, switchMap, tap, throwError} from 'rxjs';
import {LogInData} from './models/log-in-data';
import {HttpClient} from '@angular/common/http';
import {LogInResponse} from './models/log-in-response';
import {StorageService} from './storage.service';
import {handleError} from '../shared/error-handling';
import {AuthData} from './models/auth-data';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private readonly baseUrl = 'http://localhost:8080/DELETEME';

  constructor(private http: HttpClient, private storageService: StorageService) {
  }

  isLoggedIn(): Observable<boolean> {
    throw new Error('Method not implemented.');
  }

  attemptLogIn(logInData: LogInData): Observable<AuthData> {
    return this.http.post<LogInResponse>(`${this.baseUrl}/login`, logInData, {withCredentials: true})
      .pipe(
        map((response: LogInResponse): AuthData => {
          return {
            username: response.username,
            email: logInData.email
          } as AuthData;
        }),
        switchMap(authData => {
          if (!this.storageService.setAuthData(authData)) {
            return from(this.attemptLogOut()).pipe(
              switchMap(() => {
                if (this.storageService.setAuthData(authData)) return of(authData);
                else return throwError(() => new Error('Failed to override authentication data'));
              })
            );
          }
          return of(authData);
        }),
        catchError(handleError)
      );
  }

  attemptLogOut(): Observable<void> {
    return this.http.post<void>(`${this.baseUrl}/logout`, null, {withCredentials: true})
      .pipe(catchError(handleError));
  }
}
