import { beforeEach, describe, expect, it } from 'vitest';
import { provideHttpClient } from '@angular/common/http';
import { TestBed } from '@angular/core/testing';
import { TranslateLoader, TranslateModule, TranslateNoOpLoader } from '@ngx-translate/core';
import { provideToastr } from 'ngx-toastr';
import { FamService } from './fam.service';

describe('FamService', () => {
    let service: FamService;

    beforeEach(() => {
        TestBed.configureTestingModule({
            imports: [
                TranslateModule.forRoot({
                    loader: { provide: TranslateLoader, useClass: TranslateNoOpLoader }
                })
            ],
            providers: [
                provideHttpClient(),
                provideToastr()
            ]
        });
        service = TestBed.inject(FamService);
    });

    it('should be created', () => {
        expect(service).toBeTruthy();
    });
});
