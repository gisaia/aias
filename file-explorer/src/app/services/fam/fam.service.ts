import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { TranslateService } from '@ngx-translate/core';
import { Archive, DynamicFileNode } from '@tools/interface';
import { ToastrService } from 'ngx-toastr';
import { BehaviorSubject, Observable, Subject } from 'rxjs';



@Injectable({
  providedIn: 'root'
})
export class FamService {
  private options = {};
  private famSettings: { url?: string; default_path?: string; collection?: string; archives_page_size?: number, files_page_size?: number; } = {};
  public refreshArchives$: Subject<boolean> = new Subject();

  constructor(
    private http: HttpClient,
    private toastr: ToastrService,
    private translate: TranslateService
  ) { }

  dataChange = new BehaviorSubject<DynamicFileNode[]>([]);

  public setOptions(options: any) {
    this.options = options;
  }

  public setSettings(settings: any) {
    this.famSettings = settings;
  }

  public getRoot(): Observable<any> {
    return this.http.get(this.famSettings?.url + '/root', this.options);
  }

  public getFiles(path: string): Observable<any> {
    return this.http.post(this.famSettings?.url + '/files', { path, size: this.famSettings?.files_page_size }, this.options);
  }

  public getArchive(path: string): Observable<Archive[]> {
    return this.http.post(this.famSettings?.url + '/archives', { path, size: this.famSettings?.archives_page_size }, this.options) as Observable<Archive[]>;
  }

  public initializeFiles(path: string) {
    this.getFiles(path).subscribe({
      next: (data: any) => {
        const nodes: DynamicFileNode[] = [];
        data.forEach((n: any) => {
          nodes.push(this.generateNode(n, 0));
        })
        this.dataChange.next(nodes)
      },
      error: (err: Response) => {
        if (err.status === 404) {
          this.toastr.error(this.translate.instant('Unable to retrieve files'))
        } else if (err.status === 403) {
          this.toastr.warning(this.translate.instant('You are not allowed to access this feature'))
        }
      }
    })
  }

  public generateNode(object: any, level: number): DynamicFileNode {
    return new DynamicFileNode(object.name, object.path, level, object.is_dir);
  }
}
