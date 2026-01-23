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

import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { CollectionDialogComponent } from '@components/collection-dialog/collection-dialog.component';
import { DriversDialogComponent } from '@components/drivers-dialog/drivers-dialog.component';
import { TranslateService } from '@ngx-translate/core';
import { FamService } from '@services/fam/fam.service';
import { JobService } from '@services/job/job.service';
import { StatusService } from '@services/status/status.service';
import { ARLAS_AIAS_ACTIVE_COLLECTION, ARLAS_AIAS_DRIVERS_ACTIVATED } from '@tools/interface';
import { ToastrService } from 'ngx-toastr';
import { Subject } from 'rxjs';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss'],
  standalone: false
})
export class HomeComponent implements OnInit {

  public archivesPath = '';
  public collapseEvent: Subject<boolean> = new Subject();
  public refreshTasks: Subject<boolean> = new Subject();
  public showTasks = true;
  public collections: string[] = [];
  public currentCollection = '';

  constructor(
    private readonly famService: FamService,
    private readonly jobsService: JobService,
    private readonly dialog: MatDialog,
    private readonly toastr: ToastrService,
    private readonly translate: TranslateService,
    private readonly statusService: StatusService
  ) { }

  public ngOnInit(): void {
    this.jobsService.fetchAvailableDrivers();
    this.statusService.fetchExistingCollections();
    this.collections = this.statusService.existingCollections.map(c => c.id);
    this.currentCollection = localStorage.getItem(ARLAS_AIAS_ACTIVE_COLLECTION) ?? this.statusService.statusSettings.collection;
    this.addCurrentCollectionIfMissing();
    if (this.currentCollection === '') {
      this.openCatalogSelection();
    }
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
          this.toastr.success(this.translate.instant('Drivers updated'))
        }
      }
    });
  }

  public collectionChange(event) {
    localStorage.setItem(ARLAS_AIAS_ACTIVE_COLLECTION, event);
    this.currentCollection = event;
    this.famService.refreshArchives$.next(true);
  }

  public addCurrentCollectionIfMissing() {
    const newCollections = this.collections;
    if (this.currentCollection !== '' && !this.collections.includes(this.currentCollection)) {
      newCollections.push(this.currentCollection)
    }
    this.collections = [...newCollections];
  }
  
  /**
   * Refresh archives view
   */
  public refreshArchives(){
    this.famService.refreshArchives$.next(true);
  }
}
