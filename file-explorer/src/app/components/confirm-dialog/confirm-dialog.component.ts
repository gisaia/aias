import { Component, OnInit, ViewChild } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { MatInput } from '@angular/material/input';

@Component({
  selector: 'app-confirm-dialog',
  templateUrl: './confirm-dialog.component.html',
  styleUrls: ['./confirm-dialog.component.scss']
})
export class ConfirmDialogComponent implements OnInit {

  

  public title = '';
  public message = '';
  public action = '';
  public showAnnotations = true

  constructor() { }

  ngOnInit(): void {
  
  }

}
