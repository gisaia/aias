import { TestBed } from '@angular/core/testing';

import { FamService } from './fam.service';

describe('FamService', () => {
  let service: FamService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(FamService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
