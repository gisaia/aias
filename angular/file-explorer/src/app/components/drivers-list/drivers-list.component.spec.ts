import { beforeEach, describe, expect, it } from 'vitest';
import { provideHttpClient } from '@angular/common/http';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { TranslateLoader, TranslateModule, TranslateNoOpLoader } from '@ngx-translate/core';
import { provideToastr } from 'ngx-toastr';
import { DriversListComponent } from './drivers-list.component';

describe('DriversListComponent', () => {
    let component: DriversListComponent;
    let fixture: ComponentFixture<DriversListComponent>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [
                DriversListComponent,
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

        fixture = TestBed.createComponent(DriversListComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
