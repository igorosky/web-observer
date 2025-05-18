import { ComponentFixture, TestBed } from '@angular/core/testing';

import { UpdateBoxComponent } from './update-box.component';

describe('UpdateBoxComponent', () => {
  let component: UpdateBoxComponent;
  let fixture: ComponentFixture<UpdateBoxComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [UpdateBoxComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(UpdateBoxComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
