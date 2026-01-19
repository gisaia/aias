import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CollectionDialogComponent } from './collection-dialog.component';

describe('CollectionDialogComponent', () => {
  let component: CollectionDialogComponent;
  let fixture: ComponentFixture<CollectionDialogComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CollectionDialogComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CollectionDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
