import { ComponentFixture, TestBed } from '@angular/core/testing';

import { BareUpdateBoxComponent } from './bare-update-box.component';

describe('BareUpdateBoxComponent', () => {
  let component: BareUpdateBoxComponent;
  let fixture: ComponentFixture<BareUpdateBoxComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [BareUpdateBoxComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(BareUpdateBoxComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
