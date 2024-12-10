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

import { animate, state, style, transition, trigger } from '@angular/animations';
import { HttpErrorResponse } from '@angular/common/http';
import { AfterViewInit, Component, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { MatPaginator, PageEvent } from '@angular/material/paginator';
import { ConfirmDialogComponent } from '@components/confirm-dialog/confirm-dialog.component';
import { TranslateService } from '@ngx-translate/core';
import { FamService } from '@services/fam/fam.service';
import { JobService } from '@services/job/job.service';
import { Process, ProcessResult, ProcessStatus } from '@tools/interface';
import { ToastrService } from 'ngx-toastr';
import { Observable, Subject, Subscription, takeUntil, timer } from 'rxjs';

@Component({
  selector: 'app-tasks',
  templateUrl: './tasks.component.html',
  styleUrls: ['./tasks.component.scss'],
  animations: [
    trigger('detailExpand', [
      state('collapsed', style({ height: '0px', minHeight: '0' })),
      state('expanded', style({ height: '*' })),
      transition('expanded <=> collapsed', animate('225ms cubic-bezier(0.4, 0.0, 0.2, 1)')),
    ]),
  ],
})
export class TasksComponent implements OnInit, AfterViewInit, OnDestroy {

  @ViewChild(MatPaginator) public paginator!: MatPaginator;

  public tasks: Process[] = [];
  public displayedColumns: string[] = ['type', 'status', 'created', 'started', 'finished'];
  public columnsToDisplayWithExpand: string[] = [...this.displayedColumns, 'expand'];
  public expandedTask!: Process | null;

  public pageIndex = 0;
  public pageSize = 20;
  public totalProcess = 0;


  public executionObservable!: Observable<number>;
  public refreshSub!: Subscription;
  public unsubscribeRefreshTasks = new Subject<boolean>();

  public constructor(
    private jobService: JobService,
    private toastr: ToastrService,
    private translate: TranslateService,
    private famService: FamService,
    private dialog: MatDialog
  ) { }


  public ngOnInit(): void {
    this.executionObservable = timer(0, 5000);
    this.refreshSub = this.executionObservable.pipe(takeUntil(this.unsubscribeRefreshTasks)).subscribe(() => {
      this.getTasks();
    });

    this.jobService.refreshTasks.subscribe({
      next: refresh => {
        if (!!refresh) {
          this.unsubscribeRefreshTasks.next(true);
          this.pageIndex = 0;
          this.paginator.firstPage();
          this.refreshSub = this.executionObservable.pipe(takeUntil(this.unsubscribeRefreshTasks)).subscribe(() => {
            this.getTasks();
          });
        }
      }
    })

    this.jobService.refreshTasksAndArchives.subscribe({
      next: refresh => {
        if (!!refresh) {
          this.unsubscribeRefreshTasks.next(true);
          this.pageIndex = 0;
          this.paginator.firstPage();
          this.refreshSub = this.executionObservable.pipe(takeUntil(this.unsubscribeRefreshTasks)).subscribe(() => {
            this.getTasks();
            this.famService.refreshArchivesFromTasks$.next(true);
          });
        }
      }
    })

  }

  public ngAfterViewInit(): void {
    this.paginator.page.subscribe({
      next: (pe: PageEvent) => {
        this.pageIndex = pe.pageIndex;
        this.pageSize = pe.pageSize;
        this.getTasks();
      }
    });
  }

  public ngOnDestroy(): void {
    if (!!this.refreshSub) {
      this.refreshSub.unsubscribe();
    }
  }

  public getTasks() {
    this.jobService.getTasks(this.pageIndex * this.pageSize, this.pageSize).subscribe({
      next: (pr: ProcessResult) => {
        this.tasks = pr.status_list;
        this.totalProcess = pr.total;
        if (this.tasks.filter(t => t.status !== ProcessStatus.successful && t.status !== ProcessStatus.failed).length === 0) {
          this.unsubscribeRefreshTasks.next(true);
        }
      },
      error: (err: Response) => {
        if (err.status === 404) {
          this.toastr.error(this.translate.instant('Unable to retrieve status'))
        } else if (err.status === 403) {
          this.toastr.warning(this.translate.instant('You are not allowed to access this feature'))
        }
      }
    });
  }

  public cancelJob(task, jobId: string) {
    const dialogRef = this.dialog.open(ConfirmDialogComponent, { minWidth: '400px' });
    dialogRef.componentInstance.title = this.translate.instant('Confirmation');
    dialogRef.componentInstance.message = this.translate.instant('Would you like to cancel this job ?')
    dialogRef.componentInstance.action = this.translate.instant('Confirm');
    dialogRef.componentInstance.showAnnotations = false;
    dialogRef.afterClosed().subscribe({
      next: (confirm) => {
        this.jobService.cancelJob(jobId).subscribe({
          next: (p: Process) => {
            this.jobService.refreshTasks.next(true);
          },
          error: (err: HttpErrorResponse) => {
            if (err.status === 404) {
              this.toastr.error(this.translate.instant('Unable to delete this job'))
            } else if (err.status === 403) {
              this.toastr.warning(this.translate.instant('You are not allowed to access this feature'))
            } else if (err.status === 500) {
              if (!!err.error && !!err.error.detail) {
                this.toastr.error(err.error.detail);
              } else {
                this.toastr.error(this.translate.instant('Unable to delete this job'))
              }
            }
          }
        })
      }
    });
  }

}
