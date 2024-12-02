import { APP_INITIALIZER, NgModule, forwardRef } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { HttpClient, HttpClientModule } from '@angular/common/http';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatLegacyAutocompleteModule as MatAutocompleteModule } from '@angular/material/legacy-autocomplete';
import { MatLegacyButtonModule as MatButtonModule } from '@angular/material/legacy-button';
import { MatLegacyCardModule as MatCardModule } from '@angular/material/legacy-card';
import { MatLegacyCheckboxModule as MatCheckboxModule } from '@angular/material/legacy-checkbox';
import { MatLegacyChipsModule as MatChipsModule } from '@angular/material/legacy-chips';
import { MatLegacyDialogModule as MatDialogModule } from '@angular/material/legacy-dialog';
import { MatLegacyFormFieldModule as MatFormFieldModule } from '@angular/material/legacy-form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatLegacyInputModule as MatInputModule } from '@angular/material/legacy-input';
import { MatLegacyListModule as MatListModule } from '@angular/material/legacy-list';
import { MatLegacyMenuModule as MatMenuModule } from '@angular/material/legacy-menu';
import { MatLegacyPaginatorModule as MatPaginatorModule } from '@angular/material/legacy-paginator';
import { MatLegacyProgressBarModule as MatProgressBarModule } from '@angular/material/legacy-progress-bar';
import { MatLegacyProgressSpinnerModule as MatProgressSpinnerModule } from '@angular/material/legacy-progress-spinner';
import { MatLegacySelectModule as MatSelectModule } from '@angular/material/legacy-select';
import { MatSortModule } from '@angular/material/sort';
import { MatLegacyTableModule as MatTableModule } from '@angular/material/legacy-table';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatLegacyTooltipModule as MatTooltipModule } from '@angular/material/legacy-tooltip';
import { MatTreeModule } from '@angular/material/tree';
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
