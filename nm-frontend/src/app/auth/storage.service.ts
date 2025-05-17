import { Injectable } from '@angular/core';
import { AuthData } from './models/auth-data';
const AUTH_DATA_KEY = 'auth_data';
const LOG_OUT_CLEAR_KEYS = [AUTH_DATA_KEY]

@Injectable({
  providedIn: 'root'
})
export class StorageService {

  constructor() { }

  public getAuthData(): AuthData | null {
    const data: string | null = localStorage.getItem(AUTH_DATA_KEY);
    if(data === null || data.length === 0) return null;
    return JSON.parse(data) as AuthData;
  }

  public setAuthData(data: AuthData): boolean {
    if(localStorage.getItem(AUTH_DATA_KEY) !== null) return false;
    localStorage.setItem(AUTH_DATA_KEY, JSON.stringify(data));
    return true;
  }

  public clearOnLogOut(): void {
    LOG_OUT_CLEAR_KEYS.forEach(key => localStorage.removeItem(key));
  }
}
