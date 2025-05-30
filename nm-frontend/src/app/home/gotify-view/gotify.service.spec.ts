import { TestBed } from '@angular/core/testing';

import { GotifyService } from './gotify.service';

describe('GotifyService', () => {
  let service: GotifyService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(GotifyService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
