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
import { Archive, ARLAS_AIAS_COLLECTION, DynamicFileNode, IngestPayload, Process, ProcessResult } from '@tools/interface';
import { ToastrService } from 'ngx-toastr';
import { Observable, Subject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class JobService {
  private options = { headers: new HttpHeaders().set('Content-Type', 'application/json') };
  private jobSettings: { url?: string; collection?: string; catalog?: string; } = {};

  public refreshTasks: Subject<boolean> = new Subject();
  public refreshTasksAndArchives: Subject<boolean> = new Subject();

  public availableDrivers: string[] = [];

  public constructor(
    private readonly http: HttpClient,
    private readonly translate: TranslateService,
    private readonly toastr: ToastrService
  ) { }

  public setOptions(options: any) {
    this.options = options;
  }

  public setSettings(settings: any) {
    this.jobSettings = settings;
  }

  public fetchAvailableDrivers() {
    return this.http.get(this.jobSettings?.url + '/processes/ingest', this.options).subscribe({
      next: (data: any) => this.availableDrivers = data?.inputs?.include_drivers?.schema?.items?.enum,
      error: (err: HttpErrorResponse) => {
        emitErrors(
          this.toastr,
          err,
          this.translate.instant('Unable to fetch drivers'),
          this.translate.instant('You are not allowed to access this feature'),
          this.translate.instant('Error while fetching the drivers')
        );
      }
    });
  }

  public ingestArchive(archive: Archive, annotations: string, drivers: string[] = []): Observable<any> {
    const payload: IngestPayload = {
      inputs: {
        url: archive.path,
        collection: this.getCollection(),
        catalog: this.jobSettings?.catalog || 'catalog',
        annotations,
        include_drivers: drivers
      },
      outputs: null,
      response: "raw",
      subscriber: null
    }
    return this.http.post(this.jobSettings?.url + '/processes/ingest/execution', payload, this.options);
  }

  public ingestDirectory(node: DynamicFileNode, annotations: string, drivers: string[] = []) {
    const payload: IngestPayload = {
      inputs: {
        catalog: this.jobSettings?.catalog || 'catalog',
        collection: this.getCollection(),
        directory: node.path,
        annotations,
        include_drivers: drivers
      },
      outputs: null,
      response: "raw",
      subscriber: null
    }
    return this.http.post(this.jobSettings?.url + '/processes/directory_ingest/execution', payload, this.options);
  }

  public getTasks(page: number = 0, pageSize: number = 10): Observable<ProcessResult> {
    return this.http.get(this.jobSettings?.url + '/jobs?offset=' + page + '&limit=' + pageSize, this.options) as Observable<ProcessResult>;
  }

  public cancelJob(jobId: string): Observable<Process> {
    return this.http.get(this.jobSettings.url + '/jobs/' + jobId + '/cancel', this.options) as Observable<Process>;
  }

  private getCollection(): string {
    return localStorage.getItem(ARLAS_AIAS_COLLECTION) ?? this.jobSettings.collection;
  }
}
