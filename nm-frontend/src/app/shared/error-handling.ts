import { HttpErrorResponse } from '@angular/common/http';
import {Observable, throwError} from 'rxjs';

export const handleError = (error: HttpErrorResponse): Observable<never> => {
  return throwError(() => logAndExtractMessage(error));
}

export const logAndExtractMessage = (error: HttpErrorResponse): string => {
  if (error.error instanceof ErrorEvent) {
    console.error('A client error occurred:', error.error.message);
    return `An unexpected client error occurred: ${error.error.message}`;
  } else {
    const errorMessage = error.message;
    console.error(errorMessage);
    return errorMessage;
  }
}
