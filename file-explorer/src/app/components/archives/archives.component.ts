import { Component, Input, OnChanges, OnInit, Output, SimpleChanges } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { ConfirmDialogComponent } from '@components/confirm-dialog/confirm-dialog.component';
import { TranslateService } from '@ngx-translate/core';
import { FamService } from '@services/fam/fam.service';
import { JobService } from '@services/job/job.service';
import { Archive } from '@tools/interface';
import { map } from 'rxjs';

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
    private translate: TranslateService
  ) { }

  public ngOnInit(): void {

  }

  public ngOnChanges(changes: SimpleChanges): void {
    if (changes['archivesPath'] && changes['archivesPath'].currentValue !== '') {
      // TODO: use merge map to get status of each archive
      this.famService.getArchive(changes['archivesPath'].currentValue).subscribe({
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
