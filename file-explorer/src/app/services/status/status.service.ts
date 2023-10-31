import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class StatusService {
  private options = { headers: new HttpHeaders().set('Content-Type', 'application/json') };
  private statusSettings: { url?: string; collection?: string; } = {};

  constructor(
    private http: HttpClient
  ) { }

  public setOptions(options: any) {
    this.options = options;
  }

  public setSettings(settings: any) {
    this.statusSettings = settings;
  }

  public getResourceStatus(archiveId: string): Observable<any> {
    return this.http.get(
      this.statusSettings?.url + '/collections/' + this.statusSettings.collection + '/items/' + archiveId,
      this.options) as Observable<any>;
  }
}
