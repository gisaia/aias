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

import { DatePipe } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import { Component, DestroyRef, inject, input, OnChanges, OnInit, SimpleChanges } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { MatButtonModule } from '@angular/material/button';
import { MatChip, MatChipSet } from '@angular/material/chips';
import { MatDialog } from '@angular/material/dialog';
import { MatList, MatListItem } from '@angular/material/list';
import { MatTooltip } from '@angular/material/tooltip';
import { marker } from '@colsen1991/ngx-translate-extract-marker';
import { ConfirmDialogComponent } from '@components/confirm-dialog/confirm-dialog.component';
import { TranslatePipe, TranslateService } from '@ngx-translate/core';
import { FamService } from '@services/fam/fam.service';
import { JobService } from '@services/job/job.service';
import { StatusService } from '@services/status/status.service';
import { emitErrors } from '@tools/errors';
import { Archive, ARLAS_AIAS_DRIVERS_ACTIVATED, ProcessStatus } from '@tools/interface';
import { NgxSpinnerComponent, NgxSpinnerService } from 'ngx-spinner';
import { ToastrService } from 'ngx-toastr';
import { catchError, finalize, forkJoin, map, mergeMap, of, zip } from 'rxjs';
import { CopyIdComponent } from '../copy-id/copy-id.component';

@Component({
  selector: 'app-archives',
  templateUrl: './archives.component.html',
  styleUrls: ['./archives.component.scss'],
  imports: [
    MatList, MatListItem, CopyIdComponent, MatChipSet, MatButtonModule,
    MatChip, MatTooltip, NgxSpinnerComponent, DatePipe, TranslatePipe
  ]
})
export class ArchivesComponent implements OnChanges, OnInit {

  public archivesPath = input.required<string>();
  public currentCollection = input.required<string>();

  public archives: Archive[] | undefined;
  public selectedDrivers: string[] = [];

  private readonly destroyRef = inject(DestroyRef);
  public constructor(
    private readonly famService: FamService,
    private readonly jobService: JobService,
    private readonly statusService: StatusService,
    private readonly dialog: MatDialog,
    private readonly translate: TranslateService,
    private readonly spinner: NgxSpinnerService,
    private readonly toastr: ToastrService
  ) { }

  public ngOnChanges(changes: SimpleChanges): void {
    if (changes['archivesPath'] && changes['archivesPath'].currentValue !== '') {
      this.spinner.show('archives');
      this.getArchives(changes['archivesPath'].currentValue);
    }
  }

  public ngOnInit(): void {
    this.famService.refreshArchives$.pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: refresh => {
        if (!!refresh && this.archivesPath()) {
          this.spinner.show('archives');
          this.getArchives(this.archivesPath());
        }
      }
    });
    this.famService.refreshArchivesFromTasks$.pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: refresh => {
        if (!!refresh && this.archivesPath()) {
          this.getArchives(this.archivesPath());
        }
      }
    });
  }

  public getArchives(path: string) {
    const storedDrivers = localStorage.getItem(ARLAS_AIAS_DRIVERS_ACTIVATED);
    if (storedDrivers) {
      this.selectedDrivers = storedDrivers.split(',');
    }
    this.famService.getArchive(path, this.selectedDrivers)
      .pipe(
        mergeMap((archives) => {
          if (archives.length > 0) {
            return forkJoin(
              archives.map((archive: Archive) => zip(
                of(archive),
                this.statusService.getResourceStatus(archive.id).pipe(catchError(() => of([])))
              ))
            );
          } else {
            return of([]);
          }
        }),
        map(data => data.map(result => {
          const archive: Archive = result[0];
          const resourceId: any = result[1].id;
          if (resourceId) {
            archive.status = ProcessStatus.successful;
          }
          return archive;
        })),
        finalize(() => this.spinner.hide('archives'))
      )
      .subscribe({
        next: (data) => this.archives = data,
        error: (err: HttpErrorResponse) => {
          emitErrors(
            this.toastr,
            err,
            this.translate.instant('Unable to retrieve archives'),
            this.translate.instant('You are not allowed to access this feature'),
            this.translate.instant('Unable to retrieve archives')
          );
        }
      });
  }

  public activate(archive: Archive) {
    const dialogRef = this.dialog.open(ConfirmDialogComponent, { width: '600px' });
    dialogRef.componentInstance.title = this.translate.instant('Activate:', { name: archive.name });
    dialogRef.componentInstance.action = marker('Activate');
    dialogRef.afterClosed().subscribe({
      next: (confirm) => {
        if (confirm.status) {
          this.jobService.ingestArchive(archive, confirm.annotations, confirm.drivers, confirm.createOverviewCOG).subscribe({
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

  public desactivate(archive: Archive) {
    const dialogRef = this.dialog.open(ConfirmDialogComponent, { minWidth: '400px' });
    dialogRef.componentInstance.title = this.translate.instant('Dereferencing:', { name: archive.name });
    dialogRef.componentInstance.action = marker('Dereference');
    dialogRef.componentInstance.showActivationInfos = false;
    dialogRef.afterClosed().subscribe({
      next: (confirm) => {
        if (confirm.status) {
          this.statusService.dereferenceArchive(archive.id).subscribe({
            next: () => {
              this.spinner.show('archives');
              this.getArchives(this.archivesPath());
              this.toastr.success(this.translate.instant('Archive dereferenced'));
            },
            error: (err: HttpErrorResponse) => {
              emitErrors(
                this.toastr,
                err,
                this.translate.instant('Dereferencing failed'),
                this.translate.instant('You are not allowed to access this feature'),
                this.translate.instant('Dereferencing failed')
              );
            }
          });
        }
      }
    });
  }
}
