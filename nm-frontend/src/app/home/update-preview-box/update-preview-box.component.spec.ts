import { ComponentFixture, TestBed } from '@angular/core/testing';

import { UpdatePreviewBoxComponent } from './update-preview-box.component';

describe('UpdateBoxComponent', () => {
  let component: UpdatePreviewBoxComponent;
  let fixture: ComponentFixture<UpdatePreviewBoxComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [UpdatePreviewBoxComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(UpdatePreviewBoxComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
