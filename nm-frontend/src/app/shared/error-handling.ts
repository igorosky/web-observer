import { HttpErrorResponse } from '@angular/common/http';
import {Observable, throwError} from 'rxjs';

export const handleError = (error: HttpErrorResponse): Observable<never> => {
  return throwError(() => logAndExtractMessage(error));
}

export const logAndExtractMessage = (error: HttpErrorResponse): string => {
  if (error.error instanceof ErrorEvent) {
    logErrorMessage(`An unexpected client error occurred: ${error.error.message}`);
    return `An unexpected client error occurred: ${error.error.message}`;
  } else {
    const errorMessage = error.message;
    logErrorMessage(errorMessage);
    return errorMessage;
  }
}

export const logErrorMessage = (message: string)=> console.error(message);

export const convertMessageToError = (message: string) => {
  return throwError(() => logErrorMessage(message))
};
