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

import { Component } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatChipsModule } from '@angular/material/chips';
import { MatDialogModule } from '@angular/material/dialog';
import { DriversListComponent } from '@components/drivers-list/drivers-list.component';
import { TranslatePipe } from '@ngx-translate/core';

@Component({
  selector: 'app-drivers-dialog',
  imports: [MatDialogModule, MatChipsModule, TranslatePipe, MatButtonModule, DriversListComponent],
  templateUrl: './drivers-dialog.component.html',
  styleUrl: './drivers-dialog.component.scss'
})
export class DriversDialogComponent {
  public selectedDrivers: string[] = [];
}
