import { beforeEach, describe, expect, it } from 'vitest';
import { provideHttpClient } from '@angular/common/http';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { TranslateLoader, TranslateModule, TranslateNoOpLoader } from '@ngx-translate/core';
import { provideToastr } from 'ngx-toastr';
import { DriversDialogComponent } from './drivers-dialog.component';

describe('DriversDialogComponent', () => {
    let component: DriversDialogComponent;
    let fixture: ComponentFixture<DriversDialogComponent>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [
                DriversDialogComponent,
                TranslateModule.forRoot({
                    loader: { provide: TranslateLoader, useClass: TranslateNoOpLoader }
                })
            ],
            providers: [
                provideHttpClient(),
                provideToastr()
            ]
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
