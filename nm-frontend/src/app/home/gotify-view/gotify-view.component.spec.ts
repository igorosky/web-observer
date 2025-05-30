import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GotifyViewComponent } from './gotify-view.component';

describe('GotifyViewComponent', () => {
  let component: GotifyViewComponent;
  let fixture: ComponentFixture<GotifyViewComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [GotifyViewComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(GotifyViewComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
