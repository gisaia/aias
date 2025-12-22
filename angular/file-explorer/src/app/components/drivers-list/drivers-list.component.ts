import { Component, OnInit, output } from '@angular/core';
import { MatChipListboxChange, MatChipsModule } from '@angular/material/chips';
import { JobService } from '@services/job/job.service';

@Component({
  selector: 'app-drivers-list',
  standalone: true,
  imports: [MatChipsModule],
  templateUrl: './drivers-list.component.html',
  styleUrl: './drivers-list.component.scss'
})
export class DriversListComponent implements OnInit {
  public availalbleDrivers: { name: string; selected: boolean; }[] = [];
  public selectedDrivers = output<string[]>();

  public constructor(
    private readonly jobService: JobService
  ) { }

  public ngOnInit(): void {
    const storedDrivers = localStorage.getItem('driversActivated') ? localStorage.getItem('driversActivated').split(',') : [];
    this.selectedDrivers.emit(storedDrivers);
    this.availalbleDrivers = this.jobService.availableDrivers.map(driver => {
      let selected = storedDrivers.includes(driver) ?? false
      return { name: driver, selected }
    });
  }

  public driversSelectionChange(event: MatChipListboxChange) {
    this.selectedDrivers.emit(event.value.map(item => item.name));
  }
}
