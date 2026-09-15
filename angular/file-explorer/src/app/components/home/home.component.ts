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
import { Component, OnDestroy, OnInit } from '@angular/core';
import { MatIconButton } from '@angular/material/button';
import { MatDialog } from '@angular/material/dialog';
import { MatIcon } from '@angular/material/icon';
import { MatTooltip } from '@angular/material/tooltip';
import { CollectionDialogComponent } from '@components/collection-dialog/collection-dialog.component';
import { DriversDialogComponent } from '@components/drivers-dialog/drivers-dialog.component';
import { TranslatePipe, TranslateService } from '@ngx-translate/core';
import { FamService } from '@services/fam/fam.service';
import { JobService } from '@services/job/job.service';
import { StatusService } from '@services/status/status.service';
import { emitErrors } from '@tools/errors';
import { ARLAS_AIAS_ACTIVE_COLLECTION, ARLAS_AIAS_DRIVERS_ACTIVATED, ARLAS_AIAS_TASKS_PANEL_HEIGHT, Collection } from '@tools/interface';
import { TopMenuComponent } from 'arlas-wui-toolkit';
import { ToastrService } from 'ngx-toastr';
import { Subject } from 'rxjs';
import { ArchivesComponent } from '../archives/archives.component';
import { CollectionListComponent } from '../collection-list/collection-list.component';
import { ExplorerComponent } from '../explorer/explorer.component';
import { TasksComponent } from '../tasks/tasks.component';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss'],
  imports: [
    TopMenuComponent, MatIconButton, MatTooltip, MatIcon, ExplorerComponent,
    CollectionListComponent, ArchivesComponent, TasksComponent, TranslatePipe
  ]
})
export class HomeComponent implements OnInit, OnDestroy {

  public archivesPath = '';
  public collapseEvent: Subject<boolean> = new Subject();
  public refreshTasks: Subject<boolean> = new Subject();
  public showTasks = true;
  public tasksHeight = 400;
  public isResizing = false;
  public collections: string[] = [];
  public currentCollection = '';

  private startY = 0;
  private startHeight = 0;

  public constructor(
    private readonly famService: FamService,
    private readonly jobsService: JobService,
    private readonly dialog: MatDialog,
    private readonly toastr: ToastrService,
    private readonly translate: TranslateService,
    private readonly statusService: StatusService
  ) { }

  public ngOnInit(): void {
    const savedHeight = localStorage.getItem(ARLAS_AIAS_TASKS_PANEL_HEIGHT);
    if (savedHeight) {
      const parsed = Number.parseInt(savedHeight, 10);
      if (!isNaN(parsed) && parsed >= 120) {
        this.tasksHeight = parsed;
      }
    }

    this.jobsService.fetchAvailableDrivers();
    this.statusService.fetchExistingCollections().subscribe({
      next: (data: any) => {
        this.collections = data.collections.map((c: Collection) => c.id);
        this.currentCollection = localStorage.getItem(ARLAS_AIAS_ACTIVE_COLLECTION) ?? this.statusService.statusSettings.collection;
        this.addCurrentCollectionIfMissing();
        if (this.currentCollection === '') {
          this.openCatalogSelection();
        }
      },
      error: (err: HttpErrorResponse) => {
        emitErrors(
          this.toastr,
          err,
          this.translate.instant('Unable to fetch collections'),
          this.translate.instant('You are not allowed to access this feature'),
          this.translate.instant('Error while fetching the collections')
        );
      }
    });
  }

  public ngOnDestroy(): void {
    this.removeResizeListeners();
  }

  public onResizeStart(event: MouseEvent) {
    event.preventDefault();
    this.isResizing = true;
    this.startY = event.clientY;
    this.startHeight = this.tasksHeight;

    document.addEventListener('mousemove', this.onMouseMove);
    document.addEventListener('mouseup', this.onMouseUp);
    document.body.style.userSelect = 'none';
    document.body.style.cursor = 'row-resize';
  }

  private onMouseMove = (event: MouseEvent) => {
    if (!this.isResizing) {
      return;
    }
    const deltaY = this.startY - event.clientY;
    const minHeight = 120;
    const maxHeight = window.innerHeight - 150;
    this.tasksHeight = Math.min(Math.max(this.startHeight + deltaY, minHeight), maxHeight);
  };

  private onMouseUp = () => {
    if (this.isResizing) {
      this.isResizing = false;
      this.removeResizeListeners();
      document.body.style.userSelect = '';
      document.body.style.cursor = '';
      localStorage.setItem(ARLAS_AIAS_TASKS_PANEL_HEIGHT, this.tasksHeight.toString());
    }
  };

  private removeResizeListeners() {
    document.removeEventListener('mousemove', this.onMouseMove);
    document.removeEventListener('mouseup', this.onMouseUp);
  }

  public openCatalogSelection() {
    const dialogRefCollection = this.dialog.open(
      CollectionDialogComponent,
      {
        width: '400px',
        disableClose: true, data: { collections: this.collections }
      }
    );
    dialogRefCollection.afterClosed().subscribe({
      next: (confirm) => {
        if (confirm) {
          localStorage.setItem(ARLAS_AIAS_ACTIVE_COLLECTION, confirm.collection);
          this.currentCollection = confirm.collection;
          this.addCurrentCollectionIfMissing();
          this.refresh();
        }
      }
    });
  }

  public refresh() {
    this.famService.refreshArchives$.next(true);
    this.jobsService.refreshTasks.next(true);
  }

  public openDrivers() {
    const dialogRef = this.dialog.open(DriversDialogComponent, { width: '600px' });
    dialogRef.afterClosed().subscribe({
      next: (confirm) => {
        if (confirm) {
          localStorage.setItem(ARLAS_AIAS_DRIVERS_ACTIVATED, confirm.drivers);
          this.toastr.success(this.translate.instant('Drivers updated'));
        }
      }
    });
  }

  public collectionChange(event: string) {
    if (event !== '') {
      localStorage.setItem(ARLAS_AIAS_ACTIVE_COLLECTION, event);
      this.currentCollection = event;
    }
    this.famService.refreshArchives$.next(true);
  }

  public addCurrentCollectionIfMissing() {
    const newCollections = this.collections;
    if (this.currentCollection && !this.collections.includes(this.currentCollection)) {
      newCollections.push(this.currentCollection);
    }
    this.collections = [...newCollections];
  }

  /**
   * Refresh archives view
   */
  public refreshArchives() {
    this.famService.refreshArchives$.next(true);
  }
}
