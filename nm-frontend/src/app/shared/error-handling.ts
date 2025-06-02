import { HttpErrorResponse } from '@angular/common/http';
import {Observable, throwError} from 'rxjs';

export const handleError = (error: HttpErrorResponse): Observable<never> => {
  return throwError(() => logAndExtractMessage(error));
}

export const logAndExtractMessage = (error: HttpErrorResponse): string => {
  let errorMessage: string;
  if (error.error && error.error.message) {
    errorMessage = error.error.message;
  } else if (error.message) {
    errorMessage = error.message;
  } else {
    errorMessage = 'An unknown error occurred. Please try again later.';
  }
  logErrorMessage(errorMessage);
  return errorMessage;
}

export const logErrorMessage = (message: string)=> console.error(message);

export const convertMessageToError = (message: string) => {
  return throwError(() => logErrorMessage(message))
};
