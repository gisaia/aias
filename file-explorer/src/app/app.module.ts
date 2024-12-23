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

import { HttpClient, HttpClientModule } from '@angular/common/http';
import { APP_INITIALIZER, NgModule, forwardRef } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatAutocompleteModule } from '@angular/material/autocomplete';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatChipsModule } from '@angular/material/chips';
import { MatDialogModule } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatListModule } from '@angular/material/list';
import { MatMenuModule } from '@angular/material/menu';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSelectModule } from '@angular/material/select';
import { MatSortModule } from '@angular/material/sort';
import { MatTableModule } from '@angular/material/table';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatTreeModule } from '@angular/material/tree';
import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { RouterModule } from '@angular/router';
import { TranslateLoader, TranslateModule } from '@ngx-translate/core';
import { ArlasTranslateLoader } from '@tools/customLoader';
import { OAuthModule } from 'angular-oauth2-oidc';
import {
  ArlasCollaborativesearchService, ArlasConfigurationDescriptor, ArlasIamService, ArlasSettingsService,
  ArlasStartupService, ArlasToolkitSharedModule, AuthentificationService, CONFIG_UPDATER, FETCH_OPTIONS, GET_OPTIONS,
  LoginModule, PersistenceService, configUpdaterFactory, getOptionsFactory
} from 'arlas-wui-toolkit';
import { NgxSpinnerModule } from 'ngx-spinner';
import { ToastrModule } from 'ngx-toastr';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { ArchivesComponent } from './components/archives/archives.component';
import { ConfirmDialogComponent } from './components/confirm-dialog/confirm-dialog.component';
import { ExplorerComponent } from './components/explorer/explorer.component';
import { HomeComponent } from './components/home/home.component';
import { TasksComponent } from './components/tasks/tasks.component';
import { StartupService } from './services/startup.service';

export function startupServiceFactory(startupService: StartupService) {
  const init = () => startupService.init();
  return init;
}

@NgModule({
  declarations: [
    AppComponent,
    HomeComponent,
    ExplorerComponent,
    ArchivesComponent,
    TasksComponent,
    ConfirmDialogComponent
  ],
  imports: [
    BrowserModule,
    BrowserAnimationsModule,
    AppRoutingModule,
    ArlasToolkitSharedModule,
    MatAutocompleteModule,
    MatButtonModule,
    MatCardModule,
    MatCheckboxModule,
    MatChipsModule,
    MatDialogModule,
    MatFormFieldModule,
    MatIconModule,
    MatInputModule,
    MatListModule,
    MatPaginatorModule,
    MatProgressBarModule,
    MatProgressSpinnerModule,
    MatMenuModule,
    MatSelectModule,
    MatSortModule,
    MatTableModule,
    MatToolbarModule,
    MatTooltipModule,
    MatTreeModule,
    NgxSpinnerModule,
    FormsModule,
    ReactiveFormsModule,
    LoginModule,
    RouterModule,
    HttpClientModule,
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
  ],
  providers: [
    {
      provide: APP_INITIALIZER,
      useFactory: startupServiceFactory,
      deps: [StartupService],
      multi: true
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
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
