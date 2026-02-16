import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CopyIdComponent } from './copy-id.component';

describe('CopyIdComponent', () => {
  let component: CopyIdComponent;
  let fixture: ComponentFixture<CopyIdComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CopyIdComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CopyIdComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
