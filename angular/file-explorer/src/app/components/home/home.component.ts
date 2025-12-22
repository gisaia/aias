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
import { DriversDialogComponent } from '@components/drivers-dialog/drivers-dialog.component';
import { TranslateService } from '@ngx-translate/core';
import { FamService } from '@services/fam/fam.service';
import { JobService } from '@services/job/job.service';
import { ToastrService } from 'ngx-toastr';
import { Subject } from 'rxjs';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent implements OnInit {

  public archivesPath = '';
  public collapseEvent: Subject<boolean> = new Subject();
  public refreshTasks: Subject<boolean> = new Subject();
  public showTasks = true;

  constructor(
    private famService: FamService,
    private jobsService: JobService,
    private dialog: MatDialog,
    private toastr: ToastrService,
    private translate: TranslateService
  ) { }

  public ngOnInit(): void {
    this.jobsService.fetchAvailableDrivers();
  }

  public refresh() {
    this.famService.refreshArchives$.next(true);
    this.jobsService.refreshTasks.next(true);
  }

  public openDrivers() {
    const dialogRef = this.dialog.open(DriversDialogComponent, { width: '600px' });
    dialogRef.afterClosed().subscribe({
      next: (confirm) => {
        if (!!confirm) {
          localStorage.setItem('driversActivated', confirm.drivers);
          this.toastr.success(this.translate.instant('Drivers updated'))
        }
      }
    });
  }
}
