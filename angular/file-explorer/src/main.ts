/*
 * Licensed to Gisaïa under one or more contributor
 * license agreements. See the NOTICE.txt file distributed with
 * this work for additional information regarding copyright
 * ownership. Gisaïa licenses this file to you under
 * the Apache License, Version 2.0 (the "License"); you may
 * not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */

import { HttpClient, provideHttpClient, withInterceptorsFromDi } from '@angular/common/http';
import { enableProdMode, forwardRef, importProvidersFrom, inject, provideAppInitializer, provideZoneChangeDetection } from '@angular/core';
import { MAT_TOOLTIP_DEFAULT_OPTIONS } from '@angular/material/tooltip';
import { bootstrapApplication } from '@angular/platform-browser';
import { provideAnimations } from '@angular/platform-browser/animations';
import { RouterModule } from '@angular/router';
import { TranslateLoader, TranslateModule } from '@ngx-translate/core';
import { ArlasTranslateLoader } from '@tools/customLoader';
import { OAuthModule } from 'angular-oauth2-oidc';
import {
    ArlasCollaborativesearchService, ArlasConfigurationDescriptor, ArlasIamService, ArlasSettingsService,
    ArlasStartupService, ArlasToolkitSharedModule, auhtentServiceFactory, AuthentificationService, CONFIG_UPDATER,
    configUpdaterFactory, FETCH_OPTIONS, GET_OPTIONS, getOptionsFactory, iamServiceFactory, LoginModule, PersistenceService
} from 'arlas-wui-toolkit';
import { ClipboardModule } from 'ngx-clipboard';
import { NgxSpinnerModule } from 'ngx-spinner';
import { ToastrModule } from 'ngx-toastr';
import { AppRoutingModule } from './app/app-routing.module';
import { AppComponent } from './app/app.component';
import { StartupService } from './app/services/startup.service';
import { environment } from './environments/environment';

if (environment.production) {
  enableProdMode();
}

bootstrapApplication(AppComponent, {
    providers: [
        provideAnimations(),
        importProvidersFrom(
            AppRoutingModule,
            ArlasToolkitSharedModule,
            NgxSpinnerModule,
            ClipboardModule,
            LoginModule,
            RouterModule,
            ToastrModule.forRoot({
                disableTimeOut: true,
                positionClass: 'toast-bottom-right',
                preventDuplicates: true,
                closeButton: true
            }),
            TranslateModule.forRoot({
                loader: {
                    provide: TranslateLoader,
                    useClass: ArlasTranslateLoader,
                    deps: [HttpClient, ArlasSettingsService, PersistenceService]
                }
            }),
            OAuthModule.forRoot()
        ),
        provideAppInitializer(() => inject(StartupService).init()),
        {
            provide: 'AuthentificationService',
            useFactory: auhtentServiceFactory,
            deps: [AuthentificationService],
            multi: true
        },
        {
            provide: 'ArlasIamService',
            useFactory: iamServiceFactory,
            deps: [ArlasIamService],
            multi: true
        },
        {
            provide: MAT_TOOLTIP_DEFAULT_OPTIONS,
            useValue: {
                disableTooltipInteractivity: true,
                tooltipClass: 'aias-tooltip'
            },
        },
        forwardRef(() => ArlasConfigurationDescriptor),
        forwardRef(() => ArlasCollaborativesearchService),
        forwardRef(() => ArlasStartupService),
        { provide: FETCH_OPTIONS, useValue: {} },
        {
            provide: GET_OPTIONS,
            useFactory: getOptionsFactory,
            deps: [ArlasSettingsService, AuthentificationService, ArlasIamService]
        },
        {
            provide: CONFIG_UPDATER,
            useValue: configUpdaterFactory
        },
        provideHttpClient(withInterceptorsFromDi()),
        provideZoneChangeDetection()
    ]
})
  .catch(err => console.error(err));
