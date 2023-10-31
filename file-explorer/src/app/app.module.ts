import { APP_INITIALIZER, NgModule, forwardRef } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { HomeComponent } from './components/home/home.component';
import { ArlasCollaborativesearchService, ArlasConfigurationDescriptor, ArlasIamService, ArlasStartupService, ArlasToolKitModule, ArlasToolkitSharedModule, AuthentificationService, CONFIG_UPDATER, FETCH_OPTIONS, GET_OPTIONS, LoginModule, ToolkitRoutingModule, configUpdaterFactory, getOptionsFactory } from 'arlas-wui-toolkit';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatAutocompleteModule } from '@angular/material/autocomplete';
import { MatToolbarModule } from '@angular/material/toolbar';
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
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSelectModule } from '@angular/material/select';
import { MatSortModule } from '@angular/material/sort';
import { MatTableModule } from '@angular/material/table';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatTreeModule } from '@angular/material/tree';
import { RouterModule } from '@angular/router';
import { StartupService } from './services/startup.service';
import { OAuthModule } from 'angular-oauth2-oidc';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { TranslateModule, TranslateLoader } from '@ngx-translate/core';
import { TranslateHttpLoader } from '@ngx-translate/http-loader';
import { ExplorerComponent } from './components/explorer/explorer.component';
import { ArchivesComponent } from './components/archives/archives.component';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { TasksComponent } from './components/tasks/tasks.component';
import { ConfirmDialogComponent } from './components/confirm-dialog/confirm-dialog.component';
import { NgxSpinnerModule } from 'ngx-spinner';
import { ToastrModule } from 'ngx-toastr';

export function startupServiceFactory(startupService: StartupService) {
  const init = () => startupService.init();
  return init;
}

export function createTranslateLoader(http: HttpClient) {
  return new TranslateHttpLoader(http, 'assets/i18n/', '.json');
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
        useFactory: (createTranslateLoader),
        deps: [HttpClient]
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
      deps: [AuthentificationService, ArlasIamService]
    },
    {
      provide: CONFIG_UPDATER,
      useValue: configUpdaterFactory
    },
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
