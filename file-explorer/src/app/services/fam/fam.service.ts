import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';

export class DynamicFileNode {
  constructor(
    public name: string,
    public path: string,
    public level = 1,
    public is_dir = false,
    public isLoading = false,
  ) { }
}

@Injectable({
  providedIn: 'root'
})
export class FamService {
  private options = { headers: new HttpHeaders().set('Content-Type', 'application/json') };

  constructor(private http: HttpClient) { }

  dataChange = new BehaviorSubject<DynamicFileNode[]>([]);

  public setOptions(options: any) {
    this.options = options;
  }

  public getFiles(path: string): Observable<any> {
    return this.http.post('https://arlas.crts-staff.local/fam/files', { path }, this.options);
  }

  public getArchive(path: string): Observable<any> {
    return this.http.post('https://arlas.crts-staff.local/fam/archives', { path, size: 5 }, this.options);
  }

  public initialize() {
    this.getFiles('CRTS').subscribe({
      next: (data: any) => {
        const nodes: DynamicFileNode[] = [];
        data.forEach((n: any) => {
          nodes.push(this.generateNode(n, 0));
        })
        this.dataChange.next(nodes)
      }
    })
  }

  public generateNode(object: any, level: number): DynamicFileNode {
    return new DynamicFileNode(object.name, object.path, level, object.is_dir);
  }
}
