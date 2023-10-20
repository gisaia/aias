import { LOCATION_INITIALIZED } from '@angular/common';
import { Injectable, Injector } from '@angular/core';
import { TranslateService } from '@ngx-translate/core';
import { ArlasConfigService, ArlasSettings, ArlasStartupService } from 'arlas-wui-toolkit';

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
    private configService: ArlasConfigService,
    private arlasStartupService: ArlasStartupService,
    private injector: Injector,
    private translateService: TranslateService) { }

  public init(): Promise<string> {
    return this.arlasStartupService.applyAppSettings()
      .then((s: ArlasSettings) => this.arlasStartupService.authenticate(s))
      .then((s: ArlasSettings) => this.arlasStartupService.enrichHeaders(s))
      .then((s: ArlasSettings) => new Promise((resolve, reject) => {
        this.configService.setConfig({});
        resolve('Successfullly initialized app');
      }))
      // Init app with the language read from url
      .then(() => StartupService.translationLoaded(this.translateService, this.injector));
  }

  
}
