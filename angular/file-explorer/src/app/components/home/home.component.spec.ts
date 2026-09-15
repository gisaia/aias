import { provideHttpClient } from '@angular/common/http';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { TranslateLoader, TranslateModule, TranslateNoOpLoader } from '@ngx-translate/core';
import { StatusService } from '@services/status/status.service';
import { OAuthModule } from 'angular-oauth2-oidc';
import { provideToastr } from 'ngx-toastr';
import { of } from 'rxjs';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { HomeComponent } from './home.component';
import { ARLAS_AIAS_TASKS_PANEL_HEIGHT } from '@tools/interface';

describe('HomeComponent', () => {
    let component: HomeComponent;
    let fixture: ComponentFixture<HomeComponent>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [
                TranslateModule.forRoot({
                    loader: { provide: TranslateLoader, useClass: TranslateNoOpLoader }
                }),
                HomeComponent,
                OAuthModule.forRoot()
            ],
            providers: [
                provideHttpClient(),
                provideToastr(),
                {
                    provide: StatusService,
                    useValue: {
                        existingCollections: [],
                        fetchExistingCollections: vi.fn(() => of({
                            collections: []
                        })),
                        statusSettings: {
                            collection: ''
                        }
                    }
                }
            ]
        })
            .compileComponents();

        fixture = TestBed.createComponent(HomeComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });

    it('should handle task panel resizing', () => {
        component.tasksHeight = 400;
        const event = new MouseEvent('mousedown', { clientY: 500 });
        component.onResizeStart(event);
        expect(component.isResizing).toBe(true);

        const moveEvent = new MouseEvent('mousemove', { clientY: 400 });
        document.dispatchEvent(moveEvent);
        expect(component.tasksHeight).toBe(500);

        const upEvent = new MouseEvent('mouseup');
        document.dispatchEvent(upEvent);
        expect(component.isResizing).toBe(false);
        expect(localStorage.getItem(ARLAS_AIAS_TASKS_PANEL_HEIGHT)).toBe('500');
    });
});
