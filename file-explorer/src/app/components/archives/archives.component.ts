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

import { HttpErrorResponse } from '@angular/common/http';
import { Component, Input, OnChanges, OnDestroy, OnInit, SimpleChanges } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { marker } from '@colsen1991/ngx-translate-extract-marker';
import { ConfirmDialogComponent } from '@components/confirm-dialog/confirm-dialog.component';
import { TranslateService } from '@ngx-translate/core';
import { FamService } from '@services/fam/fam.service';
import { JobService } from '@services/job/job.service';
import { StatusService } from '@services/status/status.service';
import { Archive, ProcessStatus } from '@tools/interface';
import { NgxSpinnerService } from 'ngx-spinner';
import { ToastrService } from 'ngx-toastr';
import { catchError, finalize, forkJoin, map, mergeMap, of, Subject, takeUntil, zip } from 'rxjs';

@Component({
  selector: 'app-archives',
  templateUrl: './archives.component.html',
  styleUrls: ['./archives.component.scss']
})
export class ArchivesComponent implements OnChanges, OnInit, OnDestroy {

  protected onDestroy = new Subject<void>();

  @Input() public archivesPath: string = '';
  public archives: Archive[] | undefined = undefined;

  public constructor(
    private famService: FamService,
    private jobService: JobService,
    private statusService: StatusService,
    private dialog: MatDialog,
    private translate: TranslateService,
    private spinner: NgxSpinnerService,
    private toastr: ToastrService
  ) { }


  public ngOnChanges(changes: SimpleChanges): void {
    if (changes['archivesPath'] && changes['archivesPath'].currentValue !== '') {
      this.spinner.show('archives');
      this.getArchives(changes['archivesPath'].currentValue);
    }
  }

  public ngOnInit(): void {
    this.famService.refreshArchives$.pipe(takeUntil(this.onDestroy)).subscribe({
      next: refresh => {
        if (!!refresh && !!this.archivesPath && this.archivesPath !== '') {
          this.spinner.show('archives');
          this.getArchives(this.archivesPath);
        }
      }
    });
    this.famService.refreshArchivesFromTasks$.pipe(takeUntil(this.onDestroy)).subscribe({
      next: refresh => {
        if (!!refresh && !!this.archivesPath && this.archivesPath !== '') {
          this.getArchives(this.archivesPath);
        }
      }
    });
  }

  public ngOnDestroy(): void {
    this.onDestroy.next();
    this.onDestroy.complete();
  }

  public getArchives(path: string) {
    this.famService.getArchive(path)
      .pipe(
        mergeMap((archives) => {
          if (archives.length > 0) {
            return forkJoin(
              archives.map((archive: Archive) => zip(
                of(archive),
                this.statusService.getResourceStatus(archive.id).pipe(catchError(() => of([])))
              ))
            )
          } else {
            return of([]);
          }
        }),
        map(data => data.map(result => {
          const archive: Archive = result[0];
          const resourceId: any = result[1].id;
          if (!!resourceId) {
            archive.status = ProcessStatus.successful;
          }
          return archive;
        })),
        finalize(() => this.spinner.hide('archives'))
      )
      .subscribe({
        next: (data) => this.archives = data,
        error: (err: HttpErrorResponse) => {
          if (err.status === 404) {
            this.toastr.error(this.translate.instant('Unable to retrieve archives'))
          } else if (err.status === 403) {
            this.toastr.warning(this.translate.instant('You are not allowed to access this feature'))
          } else if (err.status === 500) {
            if (!!err.error && !!err.error.detail) {
              this.toastr.error(err.error.detail);
            } else {
              this.toastr.error(this.translate.instant('Unable to retrieve archives'))
            }
          }
        }
      })
  }

  public activate(archive: Archive) {
    const dialogRef = this.dialog.open(ConfirmDialogComponent, { minWidth: '400px' });
    dialogRef.componentInstance.title = this.translate.instant('Activate:', {name: archive.name});
    dialogRef.componentInstance.action = marker('Activate');
    dialogRef.afterClosed().subscribe({
      next: (confirm) => {
        if (!!confirm.status) {
          this.jobService.ingestArchive(archive, confirm.annotations).subscribe({
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
    });
  }

  public desactivate(archive: Archive) {
    const dialogRef = this.dialog.open(ConfirmDialogComponent, { minWidth: '400px' });
    dialogRef.componentInstance.title = this.translate.instant('Dereferencing:', {name: archive.name});
    dialogRef.componentInstance.action = marker('Dereference');
    dialogRef.componentInstance.showAnnotations = false;
    dialogRef.afterClosed().subscribe({
      next: (confirm) => {
        if (!!confirm.status) {
          this.statusService.dereferenceArchive(archive.id).subscribe({
            next: () => {
              this.spinner.show('archives');
              this.getArchives(this.archivesPath);
              this.toastr.success(this.translate.instant('Archive dereferenced'))
            },
            error: (err: HttpErrorResponse) => {
              if (err.status === 404) {
                this.toastr.error(this.translate.instant('Dereferencing failed'))
              } else if (err.status === 403) {
                this.toastr.warning(this.translate.instant('You are not allowed to access this feature'))
              } else if (err.status === 500) {
                if (!!err.error && !!err.error.detail) {
                  this.toastr.error(err.error.detail);
                } else {
                  this.toastr.error(this.translate.instant('Dereferencing failed'))
                }

              }
            }
          });
        }
      }
    });
  }
}
