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
