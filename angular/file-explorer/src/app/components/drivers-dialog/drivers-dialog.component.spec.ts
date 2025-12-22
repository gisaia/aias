import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DriversDialogComponent } from './drivers-dialog.component';

describe('DriversDialogComponent', () => {
  let component: DriversDialogComponent;
  let fixture: ComponentFixture<DriversDialogComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DriversDialogComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(DriversDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
