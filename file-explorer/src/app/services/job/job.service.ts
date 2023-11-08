import { HttpHeaders, HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Archive, DynamicFileNode, IngestPayload, Process, ProcessResult } from '@tools/interface';
import { ArlasSettingsService } from 'arlas-wui-toolkit';
import { Observable, Subject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class JobService {
  private options = { headers: new HttpHeaders().set('Content-Type', 'application/json') };
  private jobSettings: { url?: string; collection?: string; catalog?: string; } = {};

  public refreshTasks: Subject<boolean> = new Subject();

  constructor(
    private http: HttpClient
  ) {}

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
    return this.http.get(this.jobSettings?.url + '/jobs?offset=' + page + '&limit=' + pageSize + '&process_id=ingest', this.options) as Observable<ProcessResult>;
  }

  public getResourceStatus(archiveId: string): Observable<Process[]> {
    return this.http.get(this.jobSettings?.url + '/jobs/resources/' + archiveId, this.options) as Observable<Process[]>;
  }
}
