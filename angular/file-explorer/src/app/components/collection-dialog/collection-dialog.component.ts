import { Component, Inject } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatChipsModule } from '@angular/material/chips';
import { MatOptionModule } from '@angular/material/core';
import { MAT_DIALOG_DATA, MatDialogModule } from '@angular/material/dialog';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { CollectionListComponent } from '@components/collection-list/collection-list.component';
import { TranslateModule } from '@ngx-translate/core';

@Component({
  selector: 'app-collection-dialog',
  standalone: true,
  imports: [
    MatDialogModule, MatChipsModule, TranslateModule,
    MatSelectModule, MatOptionModule, MatButtonModule,
    MatIconModule, MatInputModule,
    CollectionListComponent
  ],
  templateUrl: './collection-dialog.component.html',
  styleUrl: './collection-dialog.component.scss'
})
export class CollectionDialogComponent {

  public collections: string[] = [];
  public selectedCollection: string;

  public constructor(
    @Inject(MAT_DIALOG_DATA) public data: any
  ) {
    this.collections = data.collections;
  }
}
