import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SiteRegisterComponent } from './site-register.component';

describe('SiteRegisterComponent', () => {
  let component: SiteRegisterComponent;
  let fixture: ComponentFixture<SiteRegisterComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SiteRegisterComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SiteRegisterComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
