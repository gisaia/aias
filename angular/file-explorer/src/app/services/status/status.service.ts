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

import { HttpClient, HttpErrorResponse, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { TranslateService } from '@ngx-translate/core';
import { emitErrors } from '@tools/errors';
import { ARLAS_AIAS_ACTIVE_COLLECTION, Collection } from '@tools/interface';
import { ToastrService } from 'ngx-toastr';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class StatusService {
  private options = { headers: new HttpHeaders().set('Content-Type', 'application/json') };
  private _statusSettings: { url?: string; collection?: string; } = {};

  public get statusSettings(): { url?: string; collection?: string; } {
    return this._statusSettings;
  }

  public existingCollections: Collection[] = [];

  public constructor(
    private readonly http: HttpClient,
    private readonly translate: TranslateService,
    private readonly toastr: ToastrService
  ) { }

  public setOptions(options: any) {
    this.options = options;
  }

  public setSettings(settings: any) {
    this._statusSettings = settings;
  }

  public getResourceStatus(archiveId: string): Observable<any> {
    return this.http.get(
      this.statusSettings?.url + '/collections/' + this.getCollection() + '/items/' + archiveId,
      this.options) as Observable<any>;
  }

  public dereferenceArchive(archiveId: string): Observable<any> {
    return this.http.delete(
      this.statusSettings?.url + '/collections/' + this.getCollection() + '/items/' + archiveId,
      this.options) as Observable<any>;
  }

  public fetchExistingCollections() {
    return this.http.get(this.statusSettings?.url + '/collections', this.options)
      .subscribe({
        next: (data: any) => this.existingCollections = data,
        error: (err: HttpErrorResponse) => {
          emitErrors(
            this.toastr,
            err,
            this.translate.instant('Unable to fetch collections'),
            this.translate.instant('You are not allowed to access this feature'),
            this.translate.instant('Error while fetching the collections')
          );
        }
      });
  }

  private getCollection(): string {
    return localStorage.getItem(ARLAS_AIAS_ACTIVE_COLLECTION) ?? this.statusSettings.collection;
  }
}
