import { Component, Input, OnChanges, Output, SimpleChanges } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { ConfirmDialogComponent } from '@components/confirm-dialog/confirm-dialog.component';
import { TranslateService } from '@ngx-translate/core';
import { FamService } from '@services/fam/fam.service';
import { JobService } from '@services/job/job.service';
import { StatusService } from '@services/status/status.service';
import { Archive, ProcessStatus } from '@tools/interface';
import { NgxSpinnerService } from 'ngx-spinner';
import { ToastrService } from 'ngx-toastr';
import { catchError, finalize, forkJoin, map, mergeMap, of, zip } from 'rxjs';

@Component({
  selector: 'app-archives',
  templateUrl: './archives.component.html',
  styleUrls: ['./archives.component.scss']
})
export class ArchivesComponent implements OnChanges {

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

  public ngOnChanges(changes: SimpleChanges): void {
    if (changes['archivesPath'] && changes['archivesPath'].currentValue !== '') {
      this.spinner.show('archives');
      this.getArchives(changes['archivesPath'].currentValue);
    }
  }

  public getArchives(path: string) {
    this.famService.getArchive(path)
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
          if (err.status === 404) {
            this.toastr.error(this.translate.instant('Unable to retrieve archives'))
          } else if (err.status === 403) {
            this.toastr.warning(this.translate.instant('You are not allowed to access this feature'))
          }
        }
      })
  }

  public activate(archive: Archive) {
    const dialogRef = this.dialog.open(ConfirmDialogComponent, { minWidth: '400px' });
    dialogRef.componentInstance.title = this.translate.instant('Activate') + ' : ' + archive.name;
    dialogRef.componentInstance.action = 'Activate';
    dialogRef.afterClosed().subscribe({
      next: (confirm) => {
        if (!!confirm.status) {
          this.jobService.ingestArchive(archive, confirm.annotations).subscribe({
            next: () => {
              this.jobService.refreshTasks.next(true);
              this.toastr.success(this.translate.instant('Activation started'))
            },
            error: (err: Response) => {
              if (err.status === 404) {
                this.toastr.error(this.translate.instant('Activation failed'))
              } else if (err.status === 403) {
                this.toastr.warning(this.translate.instant('You are not allowed to access this feature'))
              }
            }
          });
        }
      }
    });
  }

  public desactivate(archive: Archive) {
    const dialogRef = this.dialog.open(ConfirmDialogComponent, { minWidth: '400px' });
    dialogRef.componentInstance.title = this.translate.instant('Dereferencing') + ' : ' + archive.name;
    dialogRef.componentInstance.action = 'Dereference';
    dialogRef.componentInstance.showAnnotations = false;
    dialogRef.afterClosed().subscribe({
      next: (confirm) => {
        if (!!confirm.status) {
          this.statusService.dereferenceArchive(archive.id).subscribe({
            next: () => {
              this.spinner.show('archives');
              this.getArchives(this.archivesPath);
              this.toastr.success(this.translate.instant('Archive dereferenced'))
            },
            error: (err: Response) => {
              if (err.status === 404) {
                this.toastr.error(this.translate.instant('Dereferencing failed'))
              } else if (err.status === 403) {
                this.toastr.warning(this.translate.instant('You are not allowed to access this feature'))
              }
            }
          });
        }
      }
    });
  }
}
