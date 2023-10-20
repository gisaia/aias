import { FlatTreeControl } from '@angular/cdk/tree';
import { Component, OnInit } from '@angular/core';
import { DynamicDataSource } from 'src/app/tools/DynamicDataSource';
import { DynamicFileNode, FamService } from '../../services/fam/fam.service';

@Component({
  selector: 'app-explorer',
  templateUrl: './explorer.component.html',
  styleUrls: ['./explorer.component.scss']
})
export class ExplorerComponent implements OnInit {

  public treeControl: FlatTreeControl<DynamicFileNode>;
  public dataSource: DynamicDataSource;

  getLevel = (node: DynamicFileNode) => node.level;

  isExpandable = (node: DynamicFileNode) => node.is_dir;

  hasChild = (_: number, nodeData: DynamicFileNode) => nodeData.is_dir;

  constructor(
    private famService: FamService,
  ) {
    this.treeControl = new FlatTreeControl<DynamicFileNode>(this.getLevel, this.isExpandable);
    this.dataSource = new DynamicDataSource(this.treeControl, this.famService);
  }

  ngOnInit(): void {
    this.famService.dataChange.subscribe(data => {
      this.dataSource.data = data;
    });
    this.famService.initialize();
  }

}
