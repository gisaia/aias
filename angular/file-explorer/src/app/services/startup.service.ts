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

import { LOCATION_INITIALIZED } from '@angular/common';
import { Injectable, Injector } from '@angular/core';
import { TranslateService } from '@ngx-translate/core';
import { FamService } from '@services/fam/fam.service';
import { ArlasIamService, ArlasSettings, ArlasStartupService, FetchInterceptorService } from 'arlas-wui-toolkit';
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
      const url = globalThis.location.href;
      const paramLangage = 'lg';
      // Set default language to current browser language
      let langToSet = navigator.language.slice(0, 2);
      const regex = new RegExp('[?&]' + paramLangage + '(=([^&#]*)|&|#|$)');
      const results = regex.exec(url);
      if (results?.[2]) {
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
    private readonly arlasStartupService: ArlasStartupService,
    private readonly injector: Injector,
    private readonly translateService: TranslateService,
    private readonly arlasIamService: ArlasIamService,
    private readonly famService: FamService,
    private readonly jobService: JobService,
    private readonly statusService: StatusService,
    private readonly fetchInterceptorService: FetchInterceptorService
  ) { }

  public init(): Promise<string> {
    return this.arlasStartupService.applyAppSettings()
      .then((s: ArlasSettings) => this.arlasStartupService.authenticate(s))
      .then((s: ArlasSettings) => this.arlasStartupService.enrichHeaders(s))
      .then((s: ArlasSettings) => {
        this.famService.setSettings((s as any).file_manager);
        this.jobService.setSettings((s as any).jobs);
        this.statusService.setSettings((s as any).status);
        return s;
      })
      .then((settings: ArlasSettings) => new Promise((resolve, reject) => {
          const useAuthent = !!settings && !!settings.authentication
            && !!settings.authentication.use_authent;
          // The default behavior is openid, so if there is no auth_mode specified, it is openid
          const useAuthentOpenID = useAuthent && settings.authentication.auth_mode !== 'iam';
          const useAuthentIam = useAuthent && settings.authentication.auth_mode === 'iam';
          if (useAuthent) {
            this.fetchInterceptorService.applyInterceptor();
            if (useAuthentOpenID) {
              const authService = this.injector.get('AuthentificationService')[0];
              authService.canActivateProtectedRoutes.subscribe(isActivable => {
                if (isActivable) {
                  const headers = {
                    headers: {
                      Authorization: 'Bearer ' + authService.accessToken
                    }
                  };
                  this.famService.setOptions(headers);
                  this.jobService.setOptions(headers);
                  this.statusService.setOptions(headers);
                }
                resolve(settings);
              });
            } else if (useAuthentIam) {
              this.arlasIamService.tokenRefreshed$.subscribe({
                next: loginData => {
                  if (loginData) {
                    const iamHeaders = {
                      headers: {
                        Authorization: 'bearer ' + loginData.access_token,
                        'arlas-org-filter': this.arlasIamService.getOrganisation()
                      }
                    };
                    this.famService.setOptions(iamHeaders);
                    this.jobService.setOptions(iamHeaders);
                    this.statusService.setOptions(iamHeaders);
                  }
                  resolve(settings);
                }
              });
            }
          } else {
            this.famService.setOptions({});
            this.jobService.setOptions({});
            this.statusService.setOptions({});
            resolve(settings);
          }
        })

      )
      // Init app with the language read from url
      .then(() => StartupService.translationLoaded(this.translateService, this.injector));
  }
}
