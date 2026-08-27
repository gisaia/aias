import { provideHttpClient } from '@angular/common/http';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { TranslateLoader, TranslateModule, TranslateNoOpLoader } from '@ngx-translate/core';
import { provideToastr } from 'ngx-toastr';
import { beforeEach, describe, expect, it } from 'vitest';
import { ExplorerComponent } from './explorer.component';

describe('ExplorerComponent', () => {
    let component: ExplorerComponent;
    let fixture: ComponentFixture<ExplorerComponent>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            providers: [
                provideHttpClient(),
                provideToastr()
            ],
            imports: [
                TranslateModule.forRoot({
                    loader: { provide: TranslateLoader, useClass: TranslateNoOpLoader }
                }),
                ExplorerComponent
            ]
        })
            .compileComponents();

        fixture = TestBed.createComponent(ExplorerComponent);
        component = fixture.componentInstance;
        fixture.componentRef.setInput('currentCollection', 'test');
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
