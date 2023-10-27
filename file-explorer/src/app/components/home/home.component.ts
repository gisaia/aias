import { Component, OnInit } from '@angular/core';
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
    private arlasIamService: ArlasIamService
  ) { }

  ngOnInit(): void {
    this.userEmail = this.arlasIamService.user.email;
  }

  public logout() {
    this; this.arlasIamService.logout();
  }
}
