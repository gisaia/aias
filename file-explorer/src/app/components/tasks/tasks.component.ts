import { AfterViewInit, Component, Input, OnChanges, OnDestroy, OnInit, SimpleChanges, ViewChild } from '@angular/core';
import { MatPaginator, PageEvent } from '@angular/material/paginator';
import { JobService } from '@services/job/job.service';
import { Process } from '@tools/interface';
import { Observable, Subject, Subscription, takeUntil, timer } from 'rxjs';

@Component({
  selector: 'app-tasks',
  templateUrl: './tasks.component.html',
  styleUrls: ['./tasks.component.scss']
})
export class TasksComponent implements OnInit, AfterViewInit, OnDestroy {

  @ViewChild(MatPaginator) public paginator!: MatPaginator;

  public tasks: Process[] = [];
  public displayedColumns: string[] = ['type', 'status', 'created', 'started', 'finished'];

  public pageIndex = 0;
  public pageSize = 10;


  public executionObservable!: Observable<number>;
  public refreshSub!: Subscription;
  public unsubscribeRefreshTasks = new Subject<boolean>();

  public constructor(private jobService: JobService) { }


  public ngOnInit(): void {
    this.executionObservable = timer(0, 10000);
    this.refreshSub = this.executionObservable.pipe(takeUntil(this.unsubscribeRefreshTasks)).subscribe(() => {
      this.getTasks();
    });

    this.jobService.refreshTasks.subscribe({
      next: refresh => {
        if (!!refresh) {
          this.getTasks();
        }
      }
    })
  }

  public ngAfterViewInit(): void {
    this.paginator.page.subscribe({
      next: (pe: PageEvent) => {
        this.pageIndex = pe.pageIndex;
        this.pageSize = pe.pageSize;
        this.getTasks();
      }
    });
  }

  public ngOnDestroy(): void {
    if (!!this.refreshSub) {
      this.refreshSub.unsubscribe();
    }
  }

  public getTasks() {
    this.jobService.getTasks(this.pageIndex * this.pageSize, this.pageSize).subscribe({
      next: (tasks: Process[]) => this.tasks = tasks
    });
  }

}
