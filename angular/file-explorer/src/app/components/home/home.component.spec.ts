import { provideHttpClient } from '@angular/common/http';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { TranslateLoader, TranslateModule, TranslateNoOpLoader } from '@ngx-translate/core';
import { StatusService } from '@services/status/status.service';
import { OAuthModule } from 'angular-oauth2-oidc';
import { provideToastr } from 'ngx-toastr';
import { of } from 'rxjs';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { HomeComponent } from './home.component';

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
});
