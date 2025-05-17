import { TestBed } from '@angular/core/testing';

import { HomeLoaderService } from './home-loader.service';

describe('HomeLoaderService', () => {
  let service: HomeLoaderService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(HomeLoaderService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
