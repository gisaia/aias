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
