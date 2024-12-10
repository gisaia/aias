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

import { HttpHeaders, HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Archive, DynamicFileNode, IngestPayload, Process, ProcessResult } from '@tools/interface';
import { Observable, Subject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class JobService {
  private options = { headers: new HttpHeaders().set('Content-Type', 'application/json') };
  private jobSettings: { url?: string; collection?: string; catalog?: string; } = {};

  public refreshTasks: Subject<boolean> = new Subject();
  public refreshTasksAndArchives: Subject<boolean> = new Subject();

  constructor(
    private http: HttpClient
  ) { }

  public setOptions(options: any) {
    this.options = options;
  }

  public setSettings(settings: any) {
    this.jobSettings = settings;
  }

  public ingestArchive(archive: Archive, annotations: string): Observable<any> {
    const payload: IngestPayload = {
      inputs: {
        url: archive.path,
        collection: this.jobSettings?.collection || '',
        catalog: this.jobSettings?.catalog || 'catalog',
        annotations
      },
      outputs: null,
      response: "raw",
      subscriber: null
    }
    return this.http.post(this.jobSettings?.url + '/processes/ingest/execution', payload, this.options);
  }

  public ingestDirectory(node: DynamicFileNode, annotations: string) {
    const payload: IngestPayload = {
      inputs: {
        catalog: this.jobSettings?.catalog || 'catalog',
        collection: this.jobSettings?.collection || '',
        directory: node.path,
        annotations
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

  public cancelJob(jobId: string): Observable<Process>{
    return this.http.get(this.jobSettings.url + '/jobs/' + jobId + '/cancel', this.options) as Observable<Process>;
  }
}
