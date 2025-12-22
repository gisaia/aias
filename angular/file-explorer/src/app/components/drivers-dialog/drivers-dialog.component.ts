import { Component, OnInit } from '@angular/core';
import { MatChipListboxChange } from '@angular/material/chips';
import { JobService } from '@services/job/job.service';

@Component({
  selector: 'app-drivers-dialog',
  standalone: false,
  templateUrl: './drivers-dialog.component.html',
  styleUrl: './drivers-dialog.component.scss'
})
export class DriversDialogComponent implements OnInit {
  public availalbleDrivers: { name: string; selected: boolean; }[] = [];
  public selectedDrivers: string[] = [];

  public constructor(
    private jobService: JobService
  ) { }

  public ngOnInit(): void {
    const storedDrivers = localStorage.getItem('driversActivated');
    if(storedDrivers){
      this.selectedDrivers = storedDrivers.split(',');
    }
    this.availalbleDrivers = this.jobService.availableDrivers.map(driver => {
      let selected = this.selectedDrivers.includes(driver) ?? false
      return { name: driver, selected }
    });
  }

  public driversSelectionChange(event: MatChipListboxChange) {
    this.selectedDrivers = event.value.map(item => item.name);
  }
}
