import { Injectable } from '@angular/core';
import {HttpClient, HttpErrorResponse} from '@angular/common/http';
import {catchError, Observable, of, throwError} from 'rxjs';
import {handleError} from '../../shared/error-handling';

export interface GotifyData {
  url: string;
  token: string;
}

@Injectable({
  providedIn: 'root'
})
export class GotifyService {
  private readonly baseUrl = 'http://localhost:8080';

  constructor(private http: HttpClient) { }

  getGotifyData(): Observable<GotifyData | null> {
    // return this.http.get<GotifyData>(this.baseUrl + '/gotify').pipe(
    //   catchError(err => {
    //     if(err instanceof HttpErrorResponse && err.status === 404) return of(null);
    //     return handleError(err);
    //   })
    // ); todo
    return of({
      url: 'https://mail.google.com/mail/u/2/#inbox',
      token: '<PASSWORD>'
    });
  }

  updateGotifyData(newData: FormData): Observable<void> {
    return this.http.put<void>(this.baseUrl + '/gotify', newData).pipe(
      catchError(handleError)
    );
  }

  removeGotifyData(): Observable<void> {
    return this.http.delete<void>(this.baseUrl + '/gotify').pipe(catchError(handleError));
  }

}
