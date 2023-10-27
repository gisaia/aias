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
    private translate: TranslateService
  ) {
    this.treeControl = new FlatTreeControl<DynamicFileNode>(this.getLevel, this.isExpandable);
    this.dataSource = new DynamicDataSource(this.treeControl, this.famService);
  }

  ngOnInit(): void {
    this.famService.dataChange.subscribe(data => {
      this.dataSource.data = data;
    });
    this.famService.getRoot().subscribe({
      next: (root: any) => {
        this.famService.initializeFiles(root.path);
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
    const dialogRef = this.dialog.open(ConfirmDialogComponent);
    dialogRef.componentInstance.message = this.translate.instant('Do you want to activate this folder ?');
    dialogRef.componentInstance.title = this.translate.instant('Activate folder') + ' : ' + node.name;
    dialogRef.afterClosed().subscribe({
      next: (confirm) => {
        if (!!confirm) {
          this.jobService.ingestDirectory(node).subscribe({
            next: (data) => {
              this.jobService.refreshTasks.next(true);
            }
          });
        }
      }
    })
  }

}
