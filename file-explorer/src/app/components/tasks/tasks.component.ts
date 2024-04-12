import { animate, state, style, transition, trigger } from '@angular/animations';
import { AfterViewInit, Component, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { MatPaginator, PageEvent } from '@angular/material/paginator';
import { TranslateService } from '@ngx-translate/core';
import { JobService } from '@services/job/job.service';
import { Process, ProcessResult, ProcessStatus } from '@tools/interface';
import { ToastrService } from 'ngx-toastr';
import { Observable, Subject, Subscription, takeUntil, timer } from 'rxjs';

@Component({
  selector: 'app-tasks',
  templateUrl: './tasks.component.html',
  styleUrls: ['./tasks.component.scss'],
  animations: [
    trigger('detailExpand', [
      state('collapsed', style({ height: '0px', minHeight: '0' })),
      state('expanded', style({ height: '*' })),
      transition('expanded <=> collapsed', animate('225ms cubic-bezier(0.4, 0.0, 0.2, 1)')),
    ]),
  ],
})
export class TasksComponent implements OnInit, AfterViewInit, OnDestroy {

  @ViewChild(MatPaginator) public paginator!: MatPaginator;

  public tasks: Process[] = [];
  public displayedColumns: string[] = ['type', 'status', 'created', 'started', 'finished'];
  public columnsToDisplayWithExpand: string[] = [...this.displayedColumns, 'expand'];
  public expandedTask!: Process | null;

  public pageIndex = 0;
  public pageSize = 20;
  public totalProcess = 0;


  public executionObservable!: Observable<number>;
  public refreshSub!: Subscription;
  public unsubscribeRefreshTasks = new Subject<boolean>();

  public constructor(
    private jobService: JobService,
    private toastr: ToastrService,
    private translate: TranslateService
    ) { }


  public ngOnInit(): void {
    this.executionObservable = timer(0, 10000);
    this.refreshSub = this.executionObservable.pipe(takeUntil(this.unsubscribeRefreshTasks)).subscribe(() => {
      this.getTasks();
    });

    this.jobService.refreshTasks.subscribe({
      next: refresh => {
        if (!!refresh) {
          this.unsubscribeRefreshTasks.next(true);
          this.pageIndex = 0;
          this.refreshSub = this.executionObservable.pipe(takeUntil(this.unsubscribeRefreshTasks)).subscribe(() => {
            this.getTasks();
          });
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
      next: (pr: ProcessResult) => {
        this.tasks = pr.status_list;
        this.totalProcess = pr.total;
        if( this.tasks.filter(t => t.status !== ProcessStatus.successful && t.status !== ProcessStatus.failed).length === 0){
          this.unsubscribeRefreshTasks.next(true);
        }
      },
      error: (err: Response) => {
        if( err.status === 404){
          this.toastr.error(this.translate.instant('Unable to retrieve status'))
        } else if( err.status === 403){
          this.toastr.warning(this.translate.instant('You are not allowed to access this feature'))
        }
      }
    });
  }

}
