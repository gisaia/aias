import { Component, input, OnDestroy } from '@angular/core';

@Component({
  selector: 'app-copy-id',
  templateUrl: './copy-id.component.html',
  styleUrl: './copy-id.component.scss'
})
export class CopyIdComponent implements OnDestroy {
  public isCopied = false;
  public idToCopy = input<string>();

  public copied() {
    this.isCopied = true;
    // Remove copied status after 2 sec
    setTimeout(() => this.isCopied = false, 2000);
  }

  public ngOnDestroy(): void {
    this.isCopied = false
  }

}
