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
import { FamService } from '@services/fam/fam.service';
import { JobService } from '@services/job/job.service';
import { ArlasIamService } from 'arlas-wui-toolkit';
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

  public userEmail!: any;
  public isMenuOpen = false;

  constructor(
    private arlasIamService: ArlasIamService,
    private famService: FamService,
    private jobsService: JobService
  ) { }

  ngOnInit(): void {
    this.userEmail = this.arlasIamService.user.email;
  }

  public logout() {
    this.arlasIamService.logout();
  }

  public refresh() {
    this.famService.refreshArchives$.next(true);
    this.jobsService.refreshTasks.next(true);
  }
}
