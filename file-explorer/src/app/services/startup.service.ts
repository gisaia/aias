import { LOCATION_INITIALIZED } from '@angular/common';
import { Injectable, Injector } from '@angular/core';
import { TranslateService } from '@ngx-translate/core';
import { ArlasConfigService, ArlasIamService, ArlasSettings, ArlasStartupService } from 'arlas-wui-toolkit';
import { FamService } from '@services/fam/fam.service';
import { JobService } from './job/job.service';
import { StatusService } from './status/status.service';

@Injectable({
  providedIn: 'root'
})
export class StartupService {

  public contributorRegistry: Map<string, any> = new Map<string, any>();
  public interceptorRegistry: Map<string, any> = new Map<string, any>();

  public static translationLoaded(translateService: TranslateService, injector: Injector) {
    return new Promise<any>((resolve: any) => {
      const url = window.location.href;
      const paramLangage = 'lg';
      // Set default language to current browser language
      let langToSet = navigator.language.slice(0, 2);
      const regex = new RegExp('[?&]' + paramLangage + '(=([^&#]*)|&|#|$)');
      const results = regex.exec(url);
      if (results && results[2]) {
        langToSet = decodeURIComponent(results[2].replace(/\+/g, ' '));
      }
      const locationInitialized = injector.get(LOCATION_INITIALIZED, Promise.resolve(null));
      locationInitialized.then(() => {
        translateService.setDefaultLang('en');
        translateService.use(langToSet).subscribe(() => {
          console.log(`Successfully initialized '${langToSet}' language.`);
        }, () => {
          console.error(`Problem with '${langToSet}' language initialization.'`);
        }, () => {
          resolve(`Successfully initialized '${langToSet}' language.`);
        });
      });
    });
  }

  public constructor(
    private arlasStartupService: ArlasStartupService,
    private injector: Injector,
    private translateService: TranslateService,
    private arlasIamService: ArlasIamService,
    private famService: FamService,
    private jobService: JobService,
    private statusService: StatusService
    ) { }

  public init(): Promise<string> {
    return this.arlasStartupService.applyAppSettings()
      .then((s: ArlasSettings) => this.arlasStartupService.authenticate(s))
      .then((s: ArlasSettings) => this.arlasStartupService.enrichHeaders(s))
      .then((s: ArlasSettings) =>
        this.arlasIamService.tokenRefreshed$.subscribe({
          next: loginData => {
            if (!!loginData) {
              this.famService.setSettings((s as any).file_manager);
              this.famService.setOptions({
                headers: {
                  Authorization: 'bearer ' + loginData.accessToken
                }
              });
              this.jobService.setSettings((s as any).jobs);
              this.jobService.setOptions({
                headers: {
                  Authorization: 'bearer ' + loginData.accessToken
                }
              });
              this.statusService.setSettings((s as any).status);
              this.statusService.setOptions({
                headers: {
                  Authorization: 'bearer ' + loginData.accessToken
                }
              });
            }
            return Promise.resolve(s);
          }

        }))
      // Init app with the language read from url
      .then(() => StartupService.translationLoaded(this.translateService, this.injector));
  }


}
