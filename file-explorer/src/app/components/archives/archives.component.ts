import { Component, Input, OnChanges, OnInit, Output, SimpleChanges } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { ConfirmDialogComponent } from '@components/confirm-dialog/confirm-dialog.component';
import { TranslateService } from '@ngx-translate/core';
import { FamService } from '@services/fam/fam.service';
import { JobService } from '@services/job/job.service';
import { Archive, Process, ProcessStatus } from '@tools/interface';
import { NgxSpinnerService } from 'ngx-spinner';
import { finalize, forkJoin, map, mergeMap, of, zip } from 'rxjs';

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
    private dialog: MatDialog,
    private translate: TranslateService,
    private spinner: NgxSpinnerService
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
                  this.jobService.getResourceStatus(archive.id)
                ))
              )
            } else {
              return of([]);
            }
          }),
          map(data => data.map(result => {
            const archive: Archive = result[0];
            const resourceInfo: Process[] = result[1];
            if (resourceInfo.length > 0) {
              archive.status = ProcessStatus[resourceInfo[0].status];
            }
            return archive;
          })),
          finalize(() => this.spinner.hide('archives'))
        )
        .subscribe({
          next: (data) => this.archives = data
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
            next: (data) => {
              this.jobService.refreshTasks.next(true);
            }
          });
        }
      }
    });
  }

  public delete(archive: Archive) {

  }
}
