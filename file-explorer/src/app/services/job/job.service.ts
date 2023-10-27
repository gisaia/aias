import { HttpHeaders, HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Archive, DynamicFileNode, IngestPayload } from '@tools/interface';
import { ArlasSettingsService } from 'arlas-wui-toolkit';
import { Observable, Subject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class JobService {
  private options = { headers: new HttpHeaders().set('Content-Type', 'application/json') };
  private jobSettings: { url?: string; collection?: string; } = {};

  public refreshTasks: Subject<boolean> = new Subject();

  constructor(
    private http: HttpClient,
    private settingsService: ArlasSettingsService
  ) {

  }

  public setOptions(options: any) {
    this.options = options;
  }

  public setSettings(settings: any) {
    this.jobSettings = settings;
  }

  public ingestArchive(archive: Archive): Observable<any> {
    const payload: IngestPayload = {
      inputs: {
        url: archive.path,
        collection: this.jobSettings?.collection || '',
        catalog: archive.driver_name
      },
      outputs: null,
      response: "raw",
      subscriber: null
    }
    return this.http.post(this.jobSettings?.url + '/processes/ingest/execution', payload, this.options);
  }

  public ingestDirectory(node: DynamicFileNode){
    const payload: IngestPayload = {
      inputs: {
        catalog: '',
        collection: this.jobSettings?.collection || '',
        directory: node.path
      },
      outputs: null,
      response: "raw",
      subscriber: null
    }
    return this.http.post(this.jobSettings?.url + '/processes/directory_ingest/execution', payload, this.options);
  }

  public getTasks(page: number = 0, pageSize: number = 10): Observable<any> {
    return this.http.get(this.jobSettings?.url + '/jobs?page=' + page + '&page_size=' + pageSize, this.options);
  }
}
