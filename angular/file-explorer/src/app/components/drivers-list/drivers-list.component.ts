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

import { Component, OnInit, output } from '@angular/core';
import { MatChipListboxChange, MatChipsModule } from '@angular/material/chips';
import { JobService } from '@services/job/job.service';
import { ARLAS_AIAS_DRIVERS_ACTIVATED } from '@tools/interface';

interface Driver {
  name: string;
  selected: boolean;
}

@Component({
  selector: 'app-drivers-list',
  imports: [MatChipsModule],
  templateUrl: './drivers-list.component.html',
  styleUrl: './drivers-list.component.scss'
})
export class DriversListComponent implements OnInit {
  public availalbleDrivers: Driver[] = [];
  public selectedDrivers = output<string[]>();

  public constructor(
    private readonly jobService: JobService
  ) { }

  public ngOnInit(): void {
    const storedDrivers = localStorage.getItem(ARLAS_AIAS_DRIVERS_ACTIVATED)?.split(',') ?? [];
    this.selectedDrivers.emit(storedDrivers);
    this.availalbleDrivers = this.jobService.availableDrivers.map(driver => {
      let selected;
      if( localStorage.getItem(ARLAS_AIAS_DRIVERS_ACTIVATED)){
        selected = storedDrivers.includes(driver);
      } else {
        selected = true;
      }

      return { name: driver, selected };
    });
  }

  public driversSelectionChange(event: MatChipListboxChange) {
    this.selectedDrivers.emit(event.value.map((item: Driver) => item.name));
  }
}
