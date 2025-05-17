import { Injectable } from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {AuthData} from '../auth/models/auth-data';

@Injectable({
  providedIn: 'root'
})
export class HomeLoaderService {
  private readonly baseUrl = 'http://localhost:8080';

  constructor(private http: HttpClient) { }

  preloadHomeView(userData: AuthData) {
    throw new Error('Method not implemented.'); //todo
  }
}
