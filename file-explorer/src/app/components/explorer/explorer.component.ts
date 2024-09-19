import { FlatTreeControl } from '@angular/cdk/tree';
import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { DynamicDataSource } from '@tools/DynamicDataSource';
import { FamService } from '@services/fam/fam.service';
import { Subject } from 'rxjs';
import { DynamicFileNode } from '@tools/interface';
import { JobService } from '@services/job/job.service';
import { MatDialog } from '@angular/material/dialog';
import { ConfirmDialogComponent } from '@components/confirm-dialog/confirm-dialog.component';
import { TranslateService } from '@ngx-translate/core';
import { ToastrService } from 'ngx-toastr';
import { HttpErrorResponse } from '@angular/common/http';

@Component({
  selector: 'app-explorer',
  templateUrl: './explorer.component.html',
  styleUrls: ['./explorer.component.scss']
})
export class ExplorerComponent implements OnInit {


  @Output() public archivePath: EventEmitter<string> = new EventEmitter();

  @Input() public collapseAllSubject: Subject<boolean> = new Subject();

  public treeControl: FlatTreeControl<DynamicFileNode>;
  public dataSource: DynamicDataSource;

  public selectedFilePath = '';

  getLevel = (node: DynamicFileNode) => node.level;

  isExpandable = (node: DynamicFileNode) => node.is_dir;

  hasChild = (_: number, nodeData: DynamicFileNode) => nodeData.is_dir;

  constructor(
    private famService: FamService,
    private jobService: JobService,
    private dialog: MatDialog,
    private translate: TranslateService,
    private toastr: ToastrService
  ) {
    this.treeControl = new FlatTreeControl<DynamicFileNode>(this.getLevel, this.isExpandable);
    this.dataSource = new DynamicDataSource(this.treeControl, this.famService);
  }

  ngOnInit(): void {
    this.famService.dataChange.subscribe(data => {
      this.dataSource.data = data;
    });
    this.famService.getRoot().subscribe({
      next: (resp: any) => {
        this.famService.initializeFiles(resp.path);
      },
      error: (err: Response) => {
        if (err.status === 404) {
          this.toastr.error(this.translate.instant('Unable to retrieve files'))
        } else if (err.status === 403) {
          this.toastr.warning(this.translate.instant('You are not allowed to access this feature'))
        }
      }
    });
    this.collapseAllSubject.subscribe({
      next: (ok) => {
        if (!!ok) {
          this.treeControl.collapseAll();
        }
      }
    });
  }

  public listArchives(path: string) {
    this.selectedFilePath = path;
    this.archivePath.next(path);
  }

  public activate(node: DynamicFileNode) {
    const dialogRef = this.dialog.open(ConfirmDialogComponent, { minWidth: '400px' });
    dialogRef.componentInstance.title = this.translate.instant('Activate folder') + ' : ' + node.name;
    dialogRef.componentInstance.action = 'Activate';
    dialogRef.afterClosed().subscribe({
      next: (confirm) => {
        if (!!confirm.status) {
          this.jobService.ingestDirectory(node, confirm.annotations).subscribe({
            next: () => {
              this.jobService.refreshTasks.next(true);
              this.toastr.success(this.translate.instant('Activation started'))
            },
            error: (err: HttpErrorResponse) => {
              if (err.status === 404) {
                this.toastr.error(this.translate.instant('Activation failed'))
              } else if (err.status === 403) {
                this.toastr.warning(this.translate.instant('You are not allowed to access this feature'))
              } else if (err.status === 500) {
                if (!!err.error && !!err.error.detail) {
                  this.toastr.error(err.error.detail);
                } else {
                  this.toastr.error(this.translate.instant('Activation failed'))
                }
              }
            }
          });
        }
      }
    })
  }

}
