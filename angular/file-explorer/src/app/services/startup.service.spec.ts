import { provideHttpClient } from '@angular/common/http';
import { TestBed } from '@angular/core/testing';
import { TranslateLoader, TranslateModule, TranslateNoOpLoader } from '@ngx-translate/core';
import { ArlasStartupService, CONFIG_UPDATER, FETCH_OPTIONS, GET_OPTIONS } from 'arlas-wui-toolkit';
import { provideToastr } from 'ngx-toastr';
import { StartupService } from './startup.service';

describe('StartupService', () => {
  let service: StartupService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        ArlasStartupService,
        provideHttpClient(),
        provideToastr(),
        {
          provide: FETCH_OPTIONS,
          useValue: () => {}
        },
        {
          provide: GET_OPTIONS,
          useValue: () => {}
        },
        {
          provide: CONFIG_UPDATER,
          useValue: {}
        }
      ],
      imports: [
        TranslateModule.forRoot({
          loader: { provide: TranslateLoader, useClass: TranslateNoOpLoader } })
      ]
    });
    service = TestBed.inject(StartupService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
