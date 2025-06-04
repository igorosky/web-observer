import { Injectable } from '@angular/core';
import {HttpClient, HttpErrorResponse} from '@angular/common/http';
import {catchError, Observable, of} from 'rxjs';
import {handleError} from '@app/shared/error-handling';

export interface GotifyData {
  url: string;
  token: string;
}

@Injectable({
  providedIn: 'root'
})
export class GotifyService {
  private readonly baseUrl = 'http://localhost:8000';

  constructor(private http: HttpClient) { }

  getGotifyData(): Observable<GotifyData | null> {
    return this.http.get<GotifyData>(this.baseUrl + '/gotify').pipe(
      catchError(err => {
        if(err instanceof HttpErrorResponse && err.status === 404) return of(null);
        return handleError(err);
      })
    );
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
