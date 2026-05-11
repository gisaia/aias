
import { Component, ElementRef, EventEmitter, Input, OnChanges, OnInit, Output, SimpleChanges, ViewChild } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatOptionModule } from '@angular/material/core';
import { MatDividerModule } from '@angular/material/divider';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatSelect, MatSelectModule } from '@angular/material/select';
import { TranslatePipe } from '@ngx-translate/core';

@Component({
  selector: 'app-collection-list',
  imports: [
    FormsModule,
    MatFormFieldModule,
    MatSelectModule,
    MatInputModule,
    MatButtonModule,
    MatOptionModule,
    MatIconModule,
    MatDividerModule,
    TranslatePipe
],
  templateUrl: './collection-list.component.html',
  styleUrls: ['./collection-list.component.scss']
})
export class CollectionListComponent implements OnInit, OnChanges {
  @Input() public collections: string[] = [];
  @Input() public selectedValue = '';

  @Output() public selectedValueChange = new EventEmitter<string>();

  @ViewChild('select') public select!: MatSelect;
  @ViewChild('searchInput') public searchInput!: ElementRef<HTMLInputElement>;

  public searchTerm = '';
  public filteredCollections: string[] = [];

  public ngOnInit() {
    this.filteredCollections = [...this.collections];
  }

  public ngOnChanges(changes: SimpleChanges): void {
    if (changes['selectedValue']?.firstChange) {
      this.selectedValueChange.emit(changes['selectedValue'].currentValue);
    }
    if (changes['collections']) {
      this.onSearchChange();
    }
  }

  /**
   * Filters the list based on the search term
   */
  public onSearchChange() {
    const term = this.searchTerm.toLowerCase();
    this.filteredCollections = this.collections.filter(c =>
      c.toLowerCase().includes(term)
    );
  }

  /**
   * Checks if the current search term already exists in the list
   */
  public exists(): boolean {
    return this.collections.some(c => c.toLowerCase() === this.searchTerm.toLowerCase().trim());
  }

  public onSelectionChange(value: string) {
    this.selectedValue = value;
    this.selectedValueChange.emit(value);
  }

  // Regex: starts with [a-z], then [a-z0-9], total min 4 chars
  private readonly VALIDATION_REGEX = /^[a-z][a-z0-9]{3,}$/;

  /**
   * Validates the search term against the requirements
   */
  public isInvalid(): boolean {
    return !this.VALIDATION_REGEX.test(this.searchTerm);
  }

  /**
   * Adds a new value to the list and selects it
   */
  public addCustomValue() {
    if (this.searchTerm && !this.isInvalid() && !this.exists()) {
      const newValue = this.searchTerm.trim();
      this.collections.push(newValue);
      this.onSearchChange();
      this.onSelectionChange(newValue);
      this.searchTerm = '';
      this.select.close();
    }
  }

  /**
   * Handles dropdown open/close events
   */
  public onOpenedChange(opened: boolean) {
    if (opened) {
      // Auto-focus the search input when the dropdown is opened
      setTimeout(() => this.searchInput.nativeElement.focus(), 0);
    } else {
      // Reset search when closed
      this.searchTerm = '';
      this.onSearchChange();
    }
  }
}
