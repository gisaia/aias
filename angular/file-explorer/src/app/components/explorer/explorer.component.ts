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

import { FlatTreeControl } from '@angular/cdk/tree';
import { HttpErrorResponse } from '@angular/common/http';
import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatDialog } from '@angular/material/dialog';
import { MatIcon } from '@angular/material/icon';
import { MatProgressSpinner } from '@angular/material/progress-spinner';
import { MatTooltip } from '@angular/material/tooltip';
import { MatTree, MatTreeNode, MatTreeNodeDef, MatTreeNodePadding, MatTreeNodeToggle } from '@angular/material/tree';
import { marker } from '@colsen1991/ngx-translate-extract-marker';
import { ConfirmDialogComponent } from '@components/confirm-dialog/confirm-dialog.component';
import { TranslatePipe, TranslateService } from '@ngx-translate/core';
import { FamService } from '@services/fam/fam.service';
import { JobService } from '@services/job/job.service';
import { DynamicDataSource } from '@tools/DynamicDataSource';
import { emitErrors } from '@tools/errors';
import { DynamicFileNode } from '@tools/interface';
import { ToastrService } from 'ngx-toastr';
import { Subject } from 'rxjs';

@Component({
  selector: 'app-explorer',
  templateUrl: './explorer.component.html',
  styleUrls: ['./explorer.component.scss'],
  imports: [
    MatTree, MatTreeNodeDef, MatTreeNode, MatTreeNodePadding, MatButtonModule,
    MatTreeNodeToggle, MatIcon, MatTooltip, MatProgressSpinner, TranslatePipe
  ]
})
export class ExplorerComponent implements OnInit {


  @Output() public archivePath: EventEmitter<string> = new EventEmitter();

  @Input() public collapseAllSubject: Subject<boolean> = new Subject();
  @Input() public currentCollection: string;

  public treeControl: FlatTreeControl<DynamicFileNode>;
  public dataSource: DynamicDataSource;

  public selectedFilePath = '';

  public getLevel = (node: DynamicFileNode) => node.level;

  public isExpandable = (node: DynamicFileNode) => node.is_dir;

  public hasChild = (_: number, nodeData: DynamicFileNode) => nodeData.is_dir;

  public constructor(
    private readonly famService: FamService,
    private readonly jobService: JobService,
    private readonly dialog: MatDialog,
    private readonly translate: TranslateService,
    private readonly toastr: ToastrService
  ) {
    this.treeControl = new FlatTreeControl<DynamicFileNode>(this.getLevel, this.isExpandable);
    this.dataSource = new DynamicDataSource(this.treeControl, this.famService);
  }

  public ngOnInit(): void {
    this.famService.dataChange.subscribe(data => {
      this.dataSource.data = data;
    });
    this.famService.getRoot().subscribe({
      next: (resp: any) => {
        this.famService.initializeFiles(resp.path);
      },
      error: (err: Response) => {
        if (err.status === 404) {
          this.toastr.error(this.translate.instant('Unable to retrieve files'));
        } else if (err.status === 403) {
          this.toastr.warning(this.translate.instant('You are not allowed to access this feature'));
        }
      }
    });
    this.collapseAllSubject.subscribe({
      next: (ok) => {
        if (ok) {
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
    const dialogRef = this.dialog.open(ConfirmDialogComponent, { width: '600px' });
    dialogRef.componentInstance.title = this.translate.instant('Activate folder:', { folder: node.name });
    dialogRef.componentInstance.action = marker('Activate');
    dialogRef.afterClosed().subscribe({
      next: (confirm) => {
        if (confirm.status) {
          this.jobService.ingestDirectory(node, confirm.annotations, confirm.drivers).subscribe({
            next: () => {
              this.jobService.refreshTasks.next(true);
              this.toastr.success(this.translate.instant('Activation started'));
            },
            error: (err: HttpErrorResponse) => {
              emitErrors(
                this.toastr,
                err,
                this.translate.instant('Activation failed'),
                this.translate.instant('You are not allowed to access this feature'),
                this.translate.instant('Activation failed')
              );
            }
          });
        }
      }
    });
  }

}
