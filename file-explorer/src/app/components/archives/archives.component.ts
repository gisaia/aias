import { Component, Input, OnChanges, OnInit, Output, SimpleChanges } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { ConfirmDialogComponent } from '@components/confirm-dialog/confirm-dialog.component';
import { TranslateService } from '@ngx-translate/core';
import { FamService } from '@services/fam/fam.service';
import { JobService } from '@services/job/job.service';
import { StatusService } from '@services/status/status.service';
import { Archive, Process, ProcessStatus } from '@tools/interface';
import { NgxSpinnerService } from 'ngx-spinner';
import { ToastrService } from 'ngx-toastr';
import { catchError, finalize, forkJoin, map, mergeMap, of, zip } from 'rxjs';

@Component({
  selector: 'app-archives',
  templateUrl: './archives.component.html',
  styleUrls: ['./archives.component.scss']
})
export class ArchivesComponent implements OnInit, OnChanges {

  @Input() public archivesPath: string = '';
  @Output()

  public archives: Archive[] | undefined = undefined;

  public constructor(
    private famService: FamService,
    private jobService: JobService,
    private statusService: StatusService,
    private dialog: MatDialog,
    private translate: TranslateService,
    private spinner: NgxSpinnerService,
    private toastr: ToastrService
  ) { }

  public ngOnInit(): void {

  }

  public ngOnChanges(changes: SimpleChanges): void {
    if (changes['archivesPath'] && changes['archivesPath'].currentValue !== '') {
      this.spinner.show('archives');
      this.famService.getArchive(changes['archivesPath'].currentValue)
        .pipe(
          mergeMap((archives) => {
            if (archives.length > 0) {
              return forkJoin(
                archives.map((archive: Archive) => zip(
                  of(archive),
                  this.statusService.getResourceStatus(archive.id).pipe(catchError(() => of([])))
                ))
              )
            } else {
              return of([]);
            }
          }),
          map(data => data.map(result => {
            const archive: Archive = result[0];
            const resourceId: any = result[1].id;
            if (!!resourceId) {
              archive.status = ProcessStatus.successful;
            }
            return archive;
          })),
          finalize(() => this.spinner.hide('archives'))
        )
        .subscribe({
          next: (data) => this.archives = data,
          error: (err: Response) => {
            if( err.status === 404){
              this.toastr.error(this.translate.instant('Unable to retrieve archives'))
            }
            if( err.status === 403){
              this.toastr.warning(this.translate.instant('You are not allowed to access this feature'))
              // TODO: redirect to specific page
            }
          }
        })
    }
  }

  public activate(archive: Archive) {
    const dialogRef = this.dialog.open(ConfirmDialogComponent);
    dialogRef.componentInstance.message = this.translate.instant('Do you want to activate this archive ?');
    dialogRef.componentInstance.title = this.translate.instant('Activate') + ' : ' + archive.name;
    dialogRef.afterClosed().subscribe({
      next: (confirm) => {
        if (!!confirm) {
          this.jobService.ingestArchive(archive).subscribe({
            next: () => {
              this.jobService.refreshTasks.next(true);
              this.toastr.success(this.translate.instant('Activation started'))
            },
            error: (err: Response) => {
              if( err.status === 404){
                this.toastr.error(this.translate.instant('Activation failed'))
              }
              if( err.status === 403){
                this.toastr.warning(this.translate.instant('You are not allowed to access this feature'))
                // TODO: redirect to specific page
              }
            }
          });
        }
      }
    });
  }

  public delete(archive: Archive) {

  }
}
